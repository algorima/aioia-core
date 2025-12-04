/**
 * Error handling utilities for consistent API error management.
 *
 * This module provides:
 * - ERROR_CODES: Standardized error codes synced with Python backend
 * - ApiError, ServerError, ClientError: Typed error classes
 *
 * @example
 * import { ERROR_CODES, ApiError, ClientError } from '@aioia/core/errors';
 *
 * // Check error code
 * if (error instanceof ApiError && error.hasCode(ERROR_CODES.UNAUTHORIZED)) {
 *   // Handle unauthorized
 * }
 *
 * // Create typed error
 * throw new ClientError('Invalid input', ERROR_CODES.VALIDATION_ERROR, 422);
 */

// Error codes (synced with Python aioia_core.errors.error_codes)
export {
  ERROR_CODES,
  // Individual exports for tree-shaking
  UNAUTHORIZED,
  FORBIDDEN,
  INVALID_TOKEN,
  TOKEN_EXPIRED,
  JWT_SECRET_NOT_CONFIGURED,
  VALIDATION_ERROR,
  INVALID_JSON,
  MISSING_REQUIRED_FIELD,
  INVALID_QUERY_PARAMS,
  RESOURCE_NOT_FOUND,
  RESOURCE_CREATION_FAILED,
  RESOURCE_UPDATE_FAILED,
  RESOURCE_DELETE_FAILED,
  INTERNAL_SERVER_ERROR,
  DATABASE_ERROR,
  EXTERNAL_SERVICE_ERROR,
} from "./codes";
export type { ErrorCode } from "./codes";

// Error classes
export { ApiError, ServerError, ClientError } from "./exceptions";
