import { ApiError, ServerError, ClientError, ERROR_CODES } from "../errors";

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
    const error = new ServerError("Service unavailable", "EXTERNAL_SERVICE_ERROR", 503);

    expect(error.statusCode).toBe(503);
  });

  it("should be instanceof ApiError", () => {
    const error = new ServerError("Test", "TEST_CODE");

    expect(error).toBeInstanceOf(ApiError);
    expect(error).toBeInstanceOf(ServerError);
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
});

describe("ERROR_CODES", () => {
  it("should have authentication error codes", () => {
    expect(ERROR_CODES.UNAUTHORIZED).toBe("UNAUTHORIZED");
    expect(ERROR_CODES.FORBIDDEN).toBe("FORBIDDEN");
    expect(ERROR_CODES.INVALID_TOKEN).toBe("INVALID_TOKEN");
    expect(ERROR_CODES.TOKEN_EXPIRED).toBe("TOKEN_EXPIRED");
  });

  it("should have validation error codes", () => {
    expect(ERROR_CODES.VALIDATION_ERROR).toBe("VALIDATION_ERROR");
    expect(ERROR_CODES.INVALID_JSON).toBe("INVALID_JSON");
  });

  it("should have resource error codes", () => {
    expect(ERROR_CODES.RESOURCE_NOT_FOUND).toBe("RESOURCE_NOT_FOUND");
    expect(ERROR_CODES.RESOURCE_CREATION_FAILED).toBe("RESOURCE_CREATION_FAILED");
  });

  it("should have server error codes", () => {
    expect(ERROR_CODES.INTERNAL_SERVER_ERROR).toBe("INTERNAL_SERVER_ERROR");
    expect(ERROR_CODES.DATABASE_ERROR).toBe("DATABASE_ERROR");
  });
});
