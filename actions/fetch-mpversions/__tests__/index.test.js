/**
 * Unit Tests
 */

const main = require("../index");
const github = require("@actions/github");

jest.mock("@actions/github");

const mockTags = {
  data: [
    {
      name: "v1.0",
      commit: {
        sha: "123",
        url: "https://someurl",
      },
    },
  ],
};

const mockRepo = {
  owner: "test",
  repo: "repo",
};

describe("main", () => {
  let octokit;

  beforeEach(() => {
    octokit = jest.fn();
    octokit.rest = jest.fn()
    octokit.rest.repos = jest.fn();
    github.getOctokit.mockReturnValue(octokit);
    octokit.rest.repos.listTags = jest.fn();
    octokit.rest.repos.listTags.mockResolvedValue({
      data: [
        ...mockTags.data,
        {
          name: "not-a-version",
          commit: {
            sha: "asd",
            url: "https://someurl2",
          },
        },
      ],
    });
  });

  it("retrieves valid versions from tags", async () => {
    const tags = await main.getVersionsFromTags({ repo: mockRepo, octokit });
    expect(octokit.rest.repos.listTags.mock.calls).toMatchInlineSnapshot(`
      Array [
        Array [
          Object {
            "owner": "test",
            "per_page": 5,
            "repo": "repo",
          },
        ],
      ]
    `);
    expect(tags).toMatchInlineSnapshot(`
      Array [
        Object {
          "commit": Object {
            "sha": "123",
            "url": "https://someurl",
          },
          "name": "v1.0",
        },
      ]
    `);
  });

  it("retrieves recent repo versions", async () => {
    const repos = await main.getRecentVersions([mockRepo], octokit);
    expect(repos).toMatchInlineSnapshot(`
      Array [
        Object {
          "owner": "test",
          "repo": "repo",
          "versions": Array [
            Object {
              "commit": Object {
                "sha": "123",
                "url": "https://someurl",
              },
              "name": "v1.0",
            },
          ],
        },
      ]
    `);
  });

  it("parses build definition", () => {
    const builds =
      "micropython|esp32:esp8266,pycopy|someboard:anotherboard:coolboard,firmware|b1:b2";
    expect(main.parseBuilds(builds)).toMatchInlineSnapshot(`
      Object {
        "firmware": Array [
          "b1",
          "b2",
        ],
        "micropython": Array [
          "esp32",
          "esp8266",
        ],
        "pycopy": Array [
          "someboard",
          "anotherboard",
          "coolboard",
        ],
      }
    `);
  });
});
