import { INTERNAL_SERVER_ERROR } from "../errors/codes";
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

/** A request the caller cancelled through an AbortSignal is not a failure. */
const isAbortError = (error: unknown): boolean =>
  typeof error === "object" &&
  error !== null &&
  (error as { name?: unknown }).name === "AbortError";

/**
 * Wraps a failure that happened before a response could be read.
 * Caller aborts pass through unchanged.
 */
const toNetworkError = (error: unknown, url: string): unknown =>
  isAbortError(error)
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
   * Every failure is an ApiRequestError: NetworkError when no response arrives,
   * InvalidResponseError when a JSON body cannot be parsed, and whatever
   * handleError throws for an error status (ADR-0001).
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
      throw toNetworkError(error, url);
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
      throw toNetworkError(error, url);
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
   * Handles an error status. The default reads the backend error body
   * `{detail, code}` into a ServerError (5xx) or ClientError (anything else).
   * Subclasses override it for environment-specific handling such as token
   * refresh, and can reuse readApiError.
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
   * Reads the backend error body into an ApiError. A gateway in front of the
   * backend can answer with a non-JSON body, so missing fields fall back to
   * the status line and INTERNAL_SERVER_ERROR.
   * @param response The raw fetch Response object with an error status.
   */
  protected async readApiError(response: Response): Promise<ApiError> {
    const body = (await response
      .json()
      .catch(() => null)) as ApiErrorData | null;
    const message =
      body?.detail || `${response.status} ${response.statusText}`.trim();
    const code = body?.code || INTERNAL_SERVER_ERROR;

    return response.status >= 500
      ? new ServerError(message, code, response.status)
      : new ClientError(message, code, response.status);
  }
}
