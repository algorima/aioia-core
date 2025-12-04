import type { ErrorCode } from "./codes";

/**
 * Base API error class for consistent error handling.
 * Follows RFC 9457 Problem Details for HTTP APIs pattern.
 */
export class ApiError extends Error {
  /** HTTP status code */
  readonly statusCode: number;

  /** Machine-readable error code for client-side error handling */
  readonly errorCode: ErrorCode | string;

  constructor(statusCode: number, message: string, errorCode: ErrorCode | string) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.errorCode = errorCode;
    Object.setPrototypeOf(this, ApiError.prototype);
  }

  /**
   * Check if this error matches a specific error code.
   */
  hasCode(code: ErrorCode | string): boolean {
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
 */
export class ServerError extends ApiError {
  constructor(message: string, errorCode: ErrorCode | string, statusCode = 500) {
    super(statusCode, message, errorCode);
    this.name = "ServerError";
    Object.setPrototypeOf(this, ServerError.prototype);
  }
}

/**
 * Client error (4xx status codes).
 * Use for validation errors, authentication failures, or resource not found.
 */
export class ClientError extends ApiError {
  constructor(message: string, errorCode: ErrorCode | string, statusCode = 400) {
    super(statusCode, message, errorCode);
    this.name = "ClientError";
    Object.setPrototypeOf(this, ClientError.prototype);
  }
}
