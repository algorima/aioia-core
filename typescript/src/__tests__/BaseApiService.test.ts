import { BaseApiService } from "../client/BaseApiService";
import {
  ClientError,
  ERROR_CODES,
  InvalidResponseError,
  NetworkError,
  ServerError,
} from "../errors";

class TestApiService extends BaseApiService {
  protected getAuthHeaders(): Record<string, string> {
    return {};
  }
}

const URL = "https://api.example.com/api/v2/items";

const jsonResponse = (body: unknown, status = 200): Response =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

describe("BaseApiService.request", () => {
  let service: TestApiService;
  let fetchMock: jest.SpyInstance;

  beforeEach(() => {
    service = new TestApiService("https://api.example.com");
    fetchMock = jest.spyOn(global, "fetch");
  });

  afterEach(() => {
    fetchMock.mockRestore();
  });

  it("should return parsed JSON for a successful response", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ data: [1] }));

    await expect(service.request(URL)).resolves.toEqual({ data: [1] });
  });

  describe("when no response arrives", () => {
    it("should wrap a rejected fetch in NetworkError", async () => {
      const original = new TypeError("fetch failed");
      fetchMock.mockRejectedValue(original);

      const error = await service.request(URL).catch((e: unknown) => e);

      expect(error).toBeInstanceOf(NetworkError);
      expect((error as NetworkError).cause).toBe(original);
    });

    it("should wrap a failed body read in NetworkError", async () => {
      const original = new TypeError("terminated");
      fetchMock.mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ "content-type": "application/json" }),
        text: () => Promise.reject(original),
      } as unknown as Response);

      const error = await service.request(URL).catch((e: unknown) => e);

      expect(error).toBeInstanceOf(NetworkError);
      expect((error as NetworkError).cause).toBe(original);
    });

    it("should rethrow a caller abort unchanged", async () => {
      const abort = new DOMException(
        "The operation was aborted.",
        "AbortError",
      );
      fetchMock.mockRejectedValue(abort);

      await expect(service.request(URL)).rejects.toBe(abort);
    });
  });

  describe("when the response breaks the contract", () => {
    it("should throw InvalidResponseError for an unparsable JSON body", async () => {
      fetchMock.mockResolvedValue(
        new Response("<html>oops</html>", {
          status: 200,
          headers: { "content-type": "application/json" },
        }),
      );

      const error = await service.request(URL).catch((e: unknown) => e);

      expect(error).toBeInstanceOf(InvalidResponseError);
      expect((error as InvalidResponseError).cause).toBeInstanceOf(SyntaxError);
    });
  });

  describe("default handleError", () => {
    it("should read a 4xx body into ClientError", async () => {
      fetchMock.mockResolvedValue(
        jsonResponse(
          { detail: "Item not found", code: ERROR_CODES.RESOURCE_NOT_FOUND },
          404,
        ),
      );

      const error = await service.request(URL).catch((e: unknown) => e);

      expect(error).toBeInstanceOf(ClientError);
      expect(error).toMatchObject({
        message: "Item not found",
        errorCode: ERROR_CODES.RESOURCE_NOT_FOUND,
        statusCode: 404,
      });
    });

    it("should read a 5xx body into ServerError", async () => {
      fetchMock.mockResolvedValue(
        jsonResponse(
          { detail: "Database failed", code: ERROR_CODES.DATABASE_ERROR },
          500,
        ),
      );

      const error = await service.request(URL).catch((e: unknown) => e);

      expect(error).toBeInstanceOf(ServerError);
      expect(error).toMatchObject({
        message: "Database failed",
        errorCode: ERROR_CODES.DATABASE_ERROR,
        statusCode: 500,
      });
    });

    it("should fall back to the status line for a non-JSON body", async () => {
      fetchMock.mockResolvedValue(
        new Response("<html>Bad Gateway</html>", {
          status: 502,
          statusText: "Bad Gateway",
          headers: { "content-type": "text/html" },
        }),
      );

      const error = await service.request(URL).catch((e: unknown) => e);

      expect(error).toBeInstanceOf(ServerError);
      expect(error).toMatchObject({
        message: "502 Bad Gateway",
        errorCode: ERROR_CODES.INTERNAL_SERVER_ERROR,
        statusCode: 502,
      });
    });

    it("should let a subclass override handleError", async () => {
      class CustomApiService extends TestApiService {
        protected handleError(): Promise<never> {
          throw new Error("custom");
        }
      }
      fetchMock.mockResolvedValue(jsonResponse({}, 401));

      await expect(
        new CustomApiService("https://api.example.com").request(URL),
      ).rejects.toThrow("custom");
    });
  });
});
