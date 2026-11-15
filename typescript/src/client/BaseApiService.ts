import { z } from "zod";

import { INTERNAL_SERVER_ERROR, VALIDATION_ERROR } from "../errors/codes";
import {
  ApiError,
  ClientError,
  InvalidResponseError,
  NetworkError,
  ServerError,
} from "../errors/exceptions";

export interface ApiErrorData {
  code?: string;
  detail?: string;
}

/**
 * Error bodies readApiError understands. `detail` is a string (flat body),
 * an object with its own `detail` and `code` (FastAPI's default rendering of
 * an HTTPException whose detail is a dict), or a list of validation errors
 * (FastAPI's default 422).
 */
const errorBodySchema = z.object({
  code: z.string().optional(),
  detail: z
    .union([
      z.string(),
      z.object({ detail: z.string(), code: z.string().optional() }),
      z.array(z.object({ msg: z.string() })).min(1),
    ])
    .optional(),
});

const nameOf = (value: unknown): unknown =>
  typeof value === "object" && value !== null
    ? (value as { name?: unknown }).name
    : undefined;

/**
 * Whether a rejection is the caller cancelling the request. A timeout
 * (AbortSignal.timeout) is not a cancel: the response did not arrive in time.
 */
const isCallerCancel = (error: unknown, signal?: AbortSignal | null) => {
  if (signal?.aborted) return nameOf(signal.reason) !== "TimeoutError";
  return nameOf(error) === "AbortError";
};

/**
 * Wraps a failure that happened before a response could be read.
 * A caller cancel passes through unchanged.
 */
const toNetworkError = (
  error: unknown,
  url: string,
  signal?: AbortSignal | null,
): unknown =>
  isCallerCancel(error, signal)
    ? error
    : new NetworkError(`Network request failed: ${url}`, error);

/**
 * Optional error reporter interface for observability integration (e.g. Sentry).
 * Passed via constructor DI so that consumers without an error reporter (e.g. CLI)
 * can omit it without pulling in browser-specific monitoring SDKs.
 */
export interface ErrorReporter {
  captureMessage(message: string, context?: Record<string, unknown>): void;
  captureException(error: Error, context?: Record<string, unknown>): void;
}

/**
 * Base class for API services, providing common functionality for building URLs and handling requests.
 * This class is environment-agnostic and can be extended for client-side and server-side implementations.
 */
export abstract class BaseApiService {
  readonly baseUrl: string;
  readonly apiPrefix: string;
  readonly errorReporter?: ErrorReporter;

  constructor(
    baseUrl?: string,
    apiPrefix = "/api/v2",
    errorReporter?: ErrorReporter,
  ) {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || "";
    this.apiPrefix = apiPrefix;
    this.errorReporter = errorReporter;
  }

  /**
   * Builds a full URL for a given resource path.
   * @param resourcePath The path to the resource (e.g., 'users', '/companions').
   * @returns The full URL.
   */
  public buildUrl(resourcePath: string): string {
    // Remove leading slash if present to avoid double slashes
    const cleanPath = resourcePath.startsWith("/")
      ? resourcePath.slice(1)
      : resourcePath;
    const prefix = this.apiPrefix ? `${this.apiPrefix}/` : "/";
    return `${this.baseUrl}${prefix}${cleanPath}`;
  }

  /**
   * Abstract method to get authentication headers.
   * Must be implemented by subclasses to provide environment-specific authentication.
   */
  protected abstract getAuthHeaders():
    | Record<string, string>
    | Promise<Record<string, string>>;

  /**
   * Handles the logout process. Subclasses override to add environment-specific
   * sign-out logic (e.g., next-auth signOut with redirect).
   * @param message The message to log and report before signing out.
   */
  protected handleLogout(message: string): Promise<never> {
    console.warn(message);
    this.errorReporter?.captureMessage(message);
    throw new Error(message);
  }

  /**
   * Makes a request to the API.
   * Throws NetworkError when no response arrives and InvalidResponseError when
   * a JSON body cannot be parsed. An error status goes to handleError, whose
   * error is thrown as is: the request fails with an ApiRequestError only if
   * handleError throws one, which every override must do (ADR-0001).
   * A request the caller cancels rejects with the cancel reason unchanged.
   * @param url The full URL to request.
   * @param options The options for the fetch request.
   * @param isRetry Whether this is a retry attempt after session refresh (internal use).
   * @returns A promise that resolves to the JSON response, text response, or null for empty bodies.
   */
  public async request(
    url: string,
    options?: RequestInit,
    isRetry = false,
  ): Promise<unknown> {
    const headers = new Headers(options?.headers);
    const authHeaders = await this.getAuthHeaders();

    for (const [key, value] of Object.entries(authHeaders)) {
      headers.set(key, value);
    }

    let res: Response;
    try {
      res = await fetch(url, {
        ...options,
        headers,
        credentials: "include",
      });
    } catch (error) {
      throw toNetworkError(error, url, options?.signal);
    }

    if (!res.ok) {
      // Allow subclasses to handle specific error status codes
      return this.handleError(res, isRetry);
    }

    // Gracefully handle 204/205 No Content
    if (res.status === 204 || res.status === 205) {
      return null;
    }

    // Some servers omit content-length; safely read body and decide
    let text: string;
    try {
      text = await res.text();
    } catch (error) {
      throw toNetworkError(error, url, options?.signal);
    }
    if (!text) {
      return null;
    }

    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      try {
        return JSON.parse(text) as unknown;
      } catch (error) {
        throw new InvalidResponseError(
          `Response body is not valid JSON: ${url}`,
          error,
        );
      }
    }

    return text;
  }

  /**
   * Handles an error status. The default reads the backend error body into a
   * ServerError (5xx) or ClientError (anything else).
   * Subclasses override it for environment-specific handling such as token
   * refresh, and can reuse readApiError. An override must throw an
   * ApiRequestError subtype for a failed request; request does not wrap what
   * it throws, so control-flow errors such as a retry signal pass through.
   * @param response The raw fetch Response object.
   * @param _isRetry Whether this is a retry attempt after session refresh.
   */
  protected async handleError(
    response: Response,
    _isRetry: boolean,
  ): Promise<never> {
    throw await this.readApiError(response);
  }

  /**
   * Reads the backend error body into an ApiError. Only the shapes in
   * errorBodySchema are read. Anything else, such as a gateway's HTML page,
   * falls back to the status line and INTERNAL_SERVER_ERROR.
   * @param response The raw fetch Response object with an error status.
   */
  protected async readApiError(response: Response): Promise<ApiError> {
    const raw: unknown = await response.json().catch(() => null);
    const parsed = errorBodySchema.safeParse(raw);
    const body = parsed.success ? parsed.data : {};

    let message: string | undefined;
    let code = body.code;
    if (typeof body.detail === "string") {
      message = body.detail;
    } else if (Array.isArray(body.detail)) {
      message = body.detail.map((item) => item.msg).join("; ");
      code = code ?? VALIDATION_ERROR;
    } else if (body.detail) {
      message = body.detail.detail;
      code = body.detail.code ?? code;
    }

    const finalMessage =
      message || `${response.status} ${response.statusText}`.trim();
    const finalCode = code || INTERNAL_SERVER_ERROR;

    return response.status >= 500
      ? new ServerError(finalMessage, finalCode, response.status)
      : new ClientError(finalMessage, finalCode, response.status);
  }
}
