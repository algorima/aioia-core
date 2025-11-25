import { BaseCrudRepository } from "@aioia/core";
import { z } from "zod";

import { ApiService } from "@/services/api";
import type { BaseRecord } from "@/types/repository";
// 1. 테스트용 구체적인 Repository 클래스 정의
interface TestData extends BaseRecord {
  name: string;
}

const testDataSchema = z.object({
  id: z.union([z.string(), z.number()]),
  name: z.string(),
  createdAt: z.string().optional(),
  updatedAt: z.string().optional(),
});

class TestRepository extends BaseCrudRepository<TestData> {
  resource = "tests";

  protected getDataSchema() {
    return testDataSchema;
  }
}

// 2. ApiService Mock
const mockRequest = jest.fn();
const mockBuildUrl = jest
  .fn()
  .mockImplementation((path: string) => `http://api.test/api/v1/${path}`);

const mockApiService = {
  request: mockRequest,
  buildUrl: mockBuildUrl,
} as unknown as ApiService;

// 3. 테스트 시작
describe("BaseCrudRepository", () => {
  let repository: TestRepository;

  beforeEach(() => {
    // 각 테스트 전에 mock 함수들을 초기화
    jest.clearAllMocks();
    repository = new TestRepository(mockApiService);
  });

  // getList 테스트
  describe("getList", () => {
    it("should call apiService.request with correct URL and parameters", async () => {
      const params = {
        pagination: { current: 2, pageSize: 20 },
        sorters: [{ field: "name", order: "asc" as const }],
        filters: [{ field: "name", operator: "eq", value: "test" }],
      };
      const fetchOptions = { cache: "no-store" as const };

      // Mock valid response data
      const mockResponseData = {
        data: [{ id: "1", name: "Test Item" }],
        total: 1,
        pagination: { current: 2, pageSize: 20, total: 1 },
      };
      mockRequest.mockResolvedValueOnce(mockResponseData);

      await repository.getList(params, fetchOptions);

      const expectedUrl =
        "http://api.test/api/v1/tests?current=2&pageSize=20&sort=%5B%5B%22name%22%2C%22asc%22%5D%5D&filters=%5B%7B%22field%22%3A%22name%22%2C%22operator%22%3A%22eq%22%2C%22value%22%3A%22test%22%7D%5D";
      expect(mockBuildUrl).toHaveBeenCalledWith("tests");
      expect(mockRequest).toHaveBeenCalledWith(expectedUrl, fetchOptions);
    });

    it("should handle getList without any parameters", async () => {
      // Mock valid response data
      const mockResponseData = {
        data: [{ id: "1", name: "Test Item" }],
        total: 1,
      };
      mockRequest.mockResolvedValueOnce(mockResponseData);

      await repository.getList();

      const expectedUrl = "http://api.test/api/v1/tests?current=1&pageSize=10";
      expect(mockRequest).toHaveBeenCalledWith(expectedUrl, undefined);
    });
  });

  // getOne 테스트
  describe("getOne", () => {
    it("should call apiService.request with the correct URL", async () => {
      const id = "123";
      // Mock valid response data
      const mockResponseData = {
        data: { id: "123", name: "Test Item" },
      };
      mockRequest.mockResolvedValueOnce(mockResponseData);

      await repository.getOne({ id });

      const expectedUrl = "http://api.test/api/v1/tests/123";
      expect(mockBuildUrl).toHaveBeenCalledWith("tests");
      expect(mockRequest).toHaveBeenCalledWith(expectedUrl, undefined);
    });
  });

  // getMany 테스트
  describe("getMany", () => {
    it("should call apiService.request for each ID individually", async () => {
      const ids = ["1", "2", "3"];
      // Mock valid response data for individual calls
      const mockResponseData1 = {
        data: { id: "1", name: "Test Item 1" },
      };
      const mockResponseData2 = {
        data: { id: "2", name: "Test Item 2" },
      };
      const mockResponseData3 = {
        data: { id: "3", name: "Test Item 3" },
      };
      mockRequest
        .mockResolvedValueOnce(mockResponseData1)
        .mockResolvedValueOnce(mockResponseData2)
        .mockResolvedValueOnce(mockResponseData3);

      const result = await repository.getMany({ ids });

      expect(mockRequest).toHaveBeenCalledTimes(3);
      expect(mockRequest).toHaveBeenNthCalledWith(
        1,
        "http://api.test/api/v1/tests/1",
        undefined,
      );
      expect(mockRequest).toHaveBeenNthCalledWith(
        2,
        "http://api.test/api/v1/tests/2",
        undefined,
      );
      expect(mockRequest).toHaveBeenNthCalledWith(
        3,
        "http://api.test/api/v1/tests/3",
        undefined,
      );

      expect(result).toEqual({
        data: [
          { id: "1", name: "Test Item 1" },
          { id: "2", name: "Test Item 2" },
          { id: "3", name: "Test Item 3" },
        ],
      });
    });
  });

  // create 테스트
  describe("create", () => {
    it("should call apiService.request with correct parameters", async () => {
      const variables = { name: "New Item" };
      // Mock valid response data
      const mockResponseData = {
        data: { id: "new-id", name: "New Item" },
      };
      mockRequest.mockResolvedValueOnce(mockResponseData);

      await repository.create({ variables });

      const expectedUrl = "http://api.test/api/v1/tests";
      const expectedOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(variables),
      };

      expect(mockBuildUrl).toHaveBeenCalledWith("tests");
      expect(mockRequest).toHaveBeenCalledWith(expectedUrl, expectedOptions);
    });
  });

  // update 테스트
  describe("update", () => {
    it("should call apiService.request with correct parameters", async () => {
      const id = "123";
      const variables = { name: "Updated Item" };
      // Mock valid response data
      const mockResponseData = {
        data: { id: "123", name: "Updated Item" },
      };
      mockRequest.mockResolvedValueOnce(mockResponseData);

      await repository.update({ id, variables });

      const expectedUrl = "http://api.test/api/v1/tests/123";
      const expectedOptions = {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(variables),
      };

      expect(mockBuildUrl).toHaveBeenCalledWith("tests");
      expect(mockRequest).toHaveBeenCalledWith(expectedUrl, expectedOptions);
    });
  });

  // deleteOne 테스트
  describe("deleteOne", () => {
    it("should call apiService.request with correct parameters", async () => {
      const id = "123";
      // Mock valid response data
      const mockResponseData = {
        data: { id: "123", name: "Deleted Item" },
      };
      mockRequest.mockResolvedValueOnce(mockResponseData);

      await repository.deleteOne({ id });

      const expectedUrl = "http://api.test/api/v1/tests/123";
      const expectedOptions = {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      };

      expect(mockBuildUrl).toHaveBeenCalledWith("tests");
      expect(mockRequest).toHaveBeenCalledWith(expectedUrl, expectedOptions);
    });
  });

  // Schema validation tests
  describe("Schema Validation", () => {
    it("should validate getList response correctly", async () => {
      const validResponse = {
        data: [{ id: "1", name: "Valid Item" }],
        total: 1,
      };
      mockRequest.mockResolvedValueOnce(validResponse);

      const result = await repository.getList();

      expect(result).toEqual(validResponse);
    });

    it("should throw error for invalid getList response", async () => {
      const invalidResponse = {
        data: [{ id: "1", name: 123 }], // name should be string
        total: 1,
      };
      mockRequest.mockResolvedValueOnce(invalidResponse);

      await expect(repository.getList()).rejects.toThrow(
        "API response validation failed for tests",
      );
    });

    it("should validate getOne response correctly", async () => {
      const validResponse = {
        data: { id: "1", name: "Valid Item" },
      };
      mockRequest.mockResolvedValueOnce(validResponse);

      const result = await repository.getOne({ id: "1" });

      expect(result).toEqual(validResponse);
    });

    it("should throw error for invalid getOne response", async () => {
      const invalidResponse = {
        data: { id: "1" }, // missing required name field
      };
      mockRequest.mockResolvedValueOnce(invalidResponse);

      await expect(repository.getOne({ id: "1" })).rejects.toThrow(
        "API response validation failed for tests",
      );
    });

    it("should validate create response correctly", async () => {
      const validResponse = {
        data: { id: "new-id", name: "Created Item" },
      };
      mockRequest.mockResolvedValueOnce(validResponse);

      const result = await repository.create({
        variables: { name: "New Item" },
      });

      expect(result).toEqual(validResponse);
    });

    it("should throw error for missing data field in response", async () => {
      const invalidResponse = {
        total: 1, // missing data field
      };
      mockRequest.mockResolvedValueOnce(invalidResponse);

      await expect(repository.getList()).rejects.toThrow(
        "API response validation failed for tests",
      );
    });
  });
});
