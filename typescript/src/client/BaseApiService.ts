import * as Sentry from "@sentry/nextjs";

export interface ApiErrorData {
  code?: string;
  detail?: string;
}

/**
 * Base class for API services, providing common functionality for building URLs and handling requests.
 * This class is environment-agnostic and can be extended for client-side and server-side implementations.
 */
export abstract class BaseApiService {
  readonly baseUrl: string;
  readonly apiPrefix: string;

  constructor(baseUrl?: string, apiPrefix = "/api/v2") {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_BASE_URL || "";
    this.apiPrefix = apiPrefix;
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
   * Handles the logout process. Implemented as a static method to be accessible
   * without an instance, particularly in client-side scenarios where signOut is used.
   * @param message The message to log before signing out.
   */
  protected static handleLogout(message: string): Promise<never> {
    console.warn(message);
    Sentry.captureMessage(message);
    // This is a placeholder for the actual sign-out logic, which will be
    // implemented in the client-specific subclass.
    throw new Error(message);
  }

  /**
   * Makes a request to the API.
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

    const res = await fetch(url, {
      ...options,
      headers,
      credentials: "include",
    });

    if (!res.ok) {
      // Allow subclasses to handle specific error status codes
      return this.handleError(res, isRetry);
    }

    // Gracefully handle 204/205 No Content
    if (res.status === 204 || res.status === 205) {
      return null;
    }

    // Some servers omit content-length; safely read body and decide
    const text = await res.text();
    if (!text) {
      return null;
    }

    const contentType = res.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return JSON.parse(text) as unknown;
    }

    return text;
  }

  /**
   * Abstract method for handling API errors.
   * Subclasses must implement this to define specific error handling logic
   * (e.g., token refresh, redirects).
   * @param response The raw fetch Response object.
   * @param isRetry Whether this is a retry attempt after session refresh.
   */
  protected abstract handleError(
    response: Response,
    isRetry: boolean,
  ): Promise<never>;
}
