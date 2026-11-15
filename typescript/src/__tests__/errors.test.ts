import {
  ApiError,
  ApiRequestError,
  ServerError,
  ClientError,
  InvalidResponseError,
  NetworkError,
  ERROR_CODES,
} from "../errors";

describe("ApiRequestError hierarchy", () => {
  it("should put HTTP error responses under ApiRequestError", () => {
    expect(new ApiError("Test", "TEST_CODE", 400)).toBeInstanceOf(
      ApiRequestError,
    );
    expect(new ClientError("Test", "TEST_CODE")).toBeInstanceOf(
      ApiRequestError,
    );
    expect(new ServerError("Test", "TEST_CODE")).toBeInstanceOf(
      ApiRequestError,
    );
  });

  it("should keep NetworkError and InvalidResponseError out of ApiError", () => {
    const network = new NetworkError("Network request failed");
    const invalid = new InvalidResponseError("Response body is not JSON");

    expect(network).toBeInstanceOf(ApiRequestError);
    expect(network).not.toBeInstanceOf(ApiError);
    expect(invalid).toBeInstanceOf(ApiRequestError);
    expect(invalid).not.toBeInstanceOf(ApiError);
  });

  it("should keep the original error as cause", () => {
    const original = new TypeError("fetch failed");
    const error = new NetworkError("Network request failed", original);

    expect(error.cause).toBe(original);
    expect(error.name).toBe("NetworkError");
    expect(error).toBeInstanceOf(Error);
  });

  it("should name InvalidResponseError", () => {
    const error = new InvalidResponseError("bad body");

    expect(error.name).toBe("InvalidResponseError");
    expect(error.cause).toBeUndefined();
  });
});

describe("ApiError", () => {
  it("should create error with correct properties", () => {
    const error = new ApiError("Resource not found", "RESOURCE_NOT_FOUND", 404);

    expect(error.message).toBe("Resource not found");
    expect(error.errorCode).toBe("RESOURCE_NOT_FOUND");
    expect(error.statusCode).toBe(404);
    expect(error.name).toBe("ApiError");
  });

  it("should be instanceof Error", () => {
    const error = new ApiError("Test", "TEST_CODE", 400);

    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(ApiError);
  });

  describe("hasCode", () => {
    it("should return true for matching code", () => {
      const error = new ApiError("Test", ERROR_CODES.UNAUTHORIZED, 401);

      expect(error.hasCode(ERROR_CODES.UNAUTHORIZED)).toBe(true);
    });

    it("should return false for non-matching code", () => {
      const error = new ApiError("Test", ERROR_CODES.UNAUTHORIZED, 401);

      expect(error.hasCode(ERROR_CODES.FORBIDDEN)).toBe(false);
    });
  });

  describe("toJSON", () => {
    it("should serialize to RFC 9457 format", () => {
      const error = new ApiError("Invalid input", "VALIDATION_ERROR", 422);

      expect(error.toJSON()).toEqual({
        status: 422,
        detail: "Invalid input",
        code: "VALIDATION_ERROR",
      });
    });
  });
});

describe("ServerError", () => {
  it("should default to status 500", () => {
    const error = new ServerError("Database failed", "DATABASE_ERROR");

    expect(error.statusCode).toBe(500);
    expect(error.name).toBe("ServerError");
  });

  it("should allow custom status code", () => {
    const error = new ServerError(
      "Service unavailable",
      "EXTERNAL_SERVICE_ERROR",
      503,
    );

    expect(error.statusCode).toBe(503);
  });

  it("should be instanceof ApiError", () => {
    const error = new ServerError("Test", "TEST_CODE");

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toBeInstanceOf(ServerError);
  });

  it("should serialize to JSON correctly", () => {
    const error = new ServerError("Database failed", "DATABASE_ERROR", 503);

    expect(error.toJSON()).toEqual({
      status: 503,
      detail: "Database failed",
      code: "DATABASE_ERROR",
    });
  });
});

describe("ClientError", () => {
  it("should default to status 400", () => {
    const error = new ClientError("Bad request", "VALIDATION_ERROR");

    expect(error.statusCode).toBe(400);
    expect(error.name).toBe("ClientError");
  });

  it("should allow custom status code", () => {
    const error = new ClientError("Not found", "RESOURCE_NOT_FOUND", 404);

    expect(error.statusCode).toBe(404);
  });

  it("should be instanceof ApiError", () => {
    const error = new ClientError("Test", "TEST_CODE");

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toBeInstanceOf(ClientError);
  });

  it("should serialize to JSON correctly", () => {
    const error = new ClientError("Invalid input", "VALIDATION_ERROR", 422);

    expect(error.toJSON()).toEqual({
      status: 422,
      detail: "Invalid input",
      code: "VALIDATION_ERROR",
    });
  });
});
