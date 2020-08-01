/**
 * Github Action
 * Fetches latest micropython versions for building.
 */

const core = require("@actions/core");
const github = require("@actions/github");
const atob = require("atob");
const take = require("lodash").take;

const INPUTS = {
  GIT_TOKEN: "git-token",
  MAX_COUNT: "max-count",
};

const versReg = /^v?(\d+\.)?(\d+\.)?(\*|\d+)$/;

const REPOS = [
  {
    owner: "micropython",
    repo: "micropython",
  },
  {
    owner: "pfalcon",
    repo: "pycopy",
  },
];

const getVersionsFromTags = async ({ repo, octokit, count }) => {
  core.info(`Fetching tags from: ${repo.owner}/${repo.repo}`);
  const repoTags = await octokit.repos.listTags({
    ...repo,
    per_page: 5,
  });
  core.debug(`All recent tags: ${repoTags.data.map((i) => i.name).join(",")}`);
  let validTags = repoTags.data.filter((t) => {
    let vers = t.name;
    if (versReg.test(vers.trim())) {
      return vers;
    }
    core.info("FAILED REG CHECK: " + vers);
  });
  core.info(`Found recent tags: ${validTags.join(", ")}`);
  console.log(validTags[0]);
  return take(validTags, count);
};

const getRecentVersions = async (repos, octokit, count = 1) =>
  await Promise.all(
    repos.map(async (r) => ({
      ...r,
      versions: await getVersionsFromTags({ repo: r, octokit, count }),
    }))
  );

const getIDFHash = async ({ repo, version, octokit }) => {
  core.info(`Retrieving ESP-IDF hash for ${repo.repo} @ ${version}`);
  const response = await octokit.repos.getContent({
    ...repo,
    path: "ports/esp32/Makefile",
    ref: version,
  });
  let content = atob(response.data.content).split("\n");
  const hashLine = content.find((l) => l.includes("ESPIDF_SUPHASH_V4"));
  if (!hashLine) {
    return "";
  }
  const hash = hashLine.split(":=")[1].trim();
  core.info(`found ESPIDFv4 hash: ${hash}`);
  return hash;
};

const run = async () => {
  try {
    const gitToken =
      core.getInput(INPUTS.GIT_TOKEN) || process.env.GITHUB_TOKEN;
    const octokit = github.getOctokit(gitToken);
    core.startGroup("Fetch Versions");
    const maxCount = core.getInput(INPUTS.MAX_COUNT) || 1;
    const repoTags = await getRecentVersions(REPOS, octokit, maxCount);
    core.endGroup();
    core.startGroup("Determine ESP-IDF Hashes");
    let buildVersions = {};
    await Promise.all(
      repoTags.map(async (rt) => {
        buildVersions[rt.repo] = [];
        await Promise.all(
          rt.versions.map(async (v) => {
            const hash = await getIDFHash({
              repo: { owner: rt.owner, repo: rt.repo },
              version: v.name,
              octokit,
            });
            buildVersions[rt.repo].push({
              ref: v.name,
              idf: hash,
            });
          })
        );
      })
    );
    core.endGroup();
    core.info("Repository tags:", repoTags);
    core.info(buildVersions);
    core.setOutput("versions", buildVersions);
  } catch (error) {
    core.setFailed(error.message);
  }
};

run();

module.exports = {
  getVersionsFromTags,
  getRecentVersions,
};
