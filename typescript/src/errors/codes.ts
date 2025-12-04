/**
 * Error codes for consistent error handling across API endpoints.
 * These constants ensure standardized error identification for frontend applications.
 *
 * Synced with: aioia-core/python/aioia_core/errors/error_codes.py
 */

// Authentication & Authorization errors
export const UNAUTHORIZED = "UNAUTHORIZED"; // User is not authenticated
export const FORBIDDEN = "FORBIDDEN"; // User lacks permission for the requested resource
export const INVALID_TOKEN = "INVALID_TOKEN"; // JWT token is invalid or malformed
export const TOKEN_EXPIRED = "TOKEN_EXPIRED"; // JWT token has expired
export const JWT_SECRET_NOT_CONFIGURED = "JWT_SECRET_NOT_CONFIGURED"; // Server configuration error

// Validation & Request errors
export const VALIDATION_ERROR = "VALIDATION_ERROR"; // Request data validation failed
export const INVALID_JSON = "INVALID_JSON"; // Request body contains invalid JSON
export const MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"; // Required field is missing
export const INVALID_QUERY_PARAMS = "INVALID_QUERY_PARAMS"; // Query parameters are invalid

// Resource Management errors
export const RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"; // Requested resource does not exist
export const RESOURCE_CREATION_FAILED = "RESOURCE_CREATION_FAILED"; // Failed to create resource
export const RESOURCE_UPDATE_FAILED = "RESOURCE_UPDATE_FAILED"; // Failed to update resource
export const RESOURCE_DELETE_FAILED = "RESOURCE_DELETE_FAILED"; // Failed to delete resource

// System & Server errors
export const INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"; // Unexpected server error
export const DATABASE_ERROR = "DATABASE_ERROR"; // Database operation failed
export const EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"; // External service unavailable

/**
 * All error codes as a const object for type-safe access.
 * @example
 * import { ERROR_CODES } from '@aioia/core/errors';
 * if (error.code === ERROR_CODES.UNAUTHORIZED) { ... }
 */
export const ERROR_CODES = {
  // Authentication & Authorization
  UNAUTHORIZED,
  FORBIDDEN,
  INVALID_TOKEN,
  TOKEN_EXPIRED,
  JWT_SECRET_NOT_CONFIGURED,

  // Validation & Request
  VALIDATION_ERROR,
  INVALID_JSON,
  MISSING_REQUIRED_FIELD,
  INVALID_QUERY_PARAMS,

  // Resource Management
  RESOURCE_NOT_FOUND,
  RESOURCE_CREATION_FAILED,
  RESOURCE_UPDATE_FAILED,
  RESOURCE_DELETE_FAILED,

  // System & Server
  INTERNAL_SERVER_ERROR,
  DATABASE_ERROR,
  EXTERNAL_SERVICE_ERROR,
} as const;

export type ErrorCode = (typeof ERROR_CODES)[keyof typeof ERROR_CODES];
