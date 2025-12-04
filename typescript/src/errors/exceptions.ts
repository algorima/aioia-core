/**
 * Base API error class for consistent error handling.
 * Follows RFC 9457 Problem Details for HTTP APIs pattern.
 *
 * @example
 * throw new ApiError('Resource not found', 'RESOURCE_NOT_FOUND', 404);
 */
export class ApiError extends Error {
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
