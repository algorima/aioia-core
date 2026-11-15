/**
 * Root of every failure of an API request.
 * Callers treat an ApiRequestError as an expected failure and anything else
 * as a bug to rethrow (ADR-0001).
 *
 * @example
 * try {
 *   await repository.getList();
 * } catch (error) {
 *   if (!(error instanceof ApiRequestError)) throw error;
 *   // show a fallback
 * }
 */
export class ApiRequestError extends Error {
  /**
   * The error this one wraps, if any. A class field rather than ErrorOptions
   * because the build targets ES2020.
   */
  readonly cause?: unknown;

  constructor(message: string, cause?: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.cause = cause;
    Object.setPrototypeOf(this, ApiRequestError.prototype);
  }
}

/**
 * No response arrived: the request was rejected or the body stream failed.
 * A request the caller aborted is not wrapped.
 */
export class NetworkError extends ApiRequestError {
  constructor(message: string, cause?: unknown) {
    super(message, cause);
    this.name = "NetworkError";
    Object.setPrototypeOf(this, NetworkError.prototype);
  }
}

/**
 * A response arrived but broke the contract: the body could not be parsed,
 * or it failed schema validation.
 */
export class InvalidResponseError extends ApiRequestError {
  constructor(message: string, cause?: unknown) {
    super(message, cause);
    this.name = "InvalidResponseError";
    Object.setPrototypeOf(this, InvalidResponseError.prototype);
  }
}

/**
 * HTTP error response.
 * Follows RFC 9457 Problem Details for HTTP APIs pattern.
 *
 * @example
 * throw new ApiError('Resource not found', 'RESOURCE_NOT_FOUND', 404);
 */
export class ApiError extends ApiRequestError {
  /** HTTP status code */
  readonly statusCode: number;

  /** Machine-readable error code for client-side error handling */
  readonly errorCode: string;

  constructor(message: string, errorCode: string, statusCode: number) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    Object.setPrototypeOf(this, ApiError.prototype);
  }

  /**
   * Check if this error matches a specific error code.
   */
  hasCode(code: string): boolean {
    return this.errorCode === code;
  }

  /**
   * Convert to a plain object for serialization.
   */
  toJSON(): { status: number; detail: string; code: string } {
    return {
      status: this.statusCode,
      detail: this.message,
      code: this.errorCode,
    };
  }
}

/**
 * Server error (5xx status codes).
 * Use for unexpected server errors, database failures, or external service issues.
 *
 * @example
 * throw new ServerError('Database connection failed', 'DATABASE_ERROR');
 */
export class ServerError extends ApiError {
  constructor(message: string, errorCode: string, statusCode = 500) {
    super(message, errorCode, statusCode);
    this.name = "ServerError";
    Object.setPrototypeOf(this, ServerError.prototype);
  }
}

/**
 * Client error (4xx status codes).
 * Use for validation errors, authentication failures, or resource not found.
 *
 * @example
 * throw new ClientError('Invalid email format', 'VALIDATION_ERROR', 422);
 */
export class ClientError extends ApiError {
  constructor(message: string, errorCode: string, statusCode = 400) {
    super(message, errorCode, statusCode);
    this.name = "ClientError";
    Object.setPrototypeOf(this, ClientError.prototype);
  }
}
