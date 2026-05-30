const fs = require("fs");

const canonicalUrls = [
"https://automoto.com.lv/lv/jauni-auto",
"https://automoto.com.lv/lv/jauni-auto/audi",
"https://automoto.com.lv/lv/jauni-auto/audi/a3",
"https://automoto.com.lv/lv/jauni-auto/audi/a3/2020",
"https://automoto.com.lv/ru/novye-avto",
"https://automoto.com.lv/ru/novye-avto/audi",
"https://automoto.com.lv/ru/novye-avto/audi/a3",
"https://automoto.com.lv/ru/novye-avto/audi/a3/2020",
"https://automoto.com.lv/en/new-cars",
"https://automoto.com.lv/en/new-cars/audi",
"https://automoto.com.lv/en/new-cars/audi/a3",
"https://automoto.com.lv/en/new-cars/audi/a3/2020"
];

// =========================
// helpers
// =========================

function csvEscape(value) {
  const str = String(value ?? "");
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function normalizeUrl(url) {
  const u = new URL(url);

  if (u.pathname.length > 1 && u.pathname.endsWith("/")) {
    u.pathname = u.pathname.slice(0, -1);
  }

  return u.toString();
}

function isLanguageRootUrl(url) {
  const u = new URL(url);
  return ["/lv", "/lv/", "/ru", "/ru/", "/en", "/en/"].includes(u.pathname);
}

function addTrailingSlash(url) {
  return url.endsWith("/") ? url : `${url}/`;
}

function toHttp(url) {
  return url.replace(/^https:\/\//i, "http://");
}

function addWww(url) {
  return url.replace(/^https?:\/\/(?!www\.)/i, match => `${match}www.`);
}

function splitPathParts(url) {
  const u = new URL(url);
  return u.pathname.split("/").filter(Boolean);
}

// =========================
// mutations
// =========================

function uppercasePath(url) {
  const u = new URL(url);
  const parts = splitPathParts(url);

  if (parts.length > 1) {
    const lang = parts[0];
    const rest = parts.slice(1).map(part => part.toUpperCase());
    u.pathname = "/" + [lang, ...rest].join("/");
  }

  return u.toString();
}

function replaceHyphenWithUnderscore(url) {
  const u = new URL(url);
  const parts = splitPathParts(url);

  if (parts.length > 1) {
    const lang = parts[0];
    const rest = parts.slice(1).map(part => part.replace(/-/g, "_"));
    u.pathname = "/" + [lang, ...rest].join("/");
  }

  return u.toString();
}

function replaceHyphenWithPercent20(url) {
  const u = new URL(url);
  const parts = splitPathParts(url);

  if (parts.length > 1) {
    const lang = parts[0];
    const rest = parts.slice(1).map(part => part.replace(/-/g, "%20"));
    const newPath = "/" + [lang, ...rest].join("/");
    return `${u.origin}${newPath}${u.search}${u.hash}`;
  }

  return url;
}

// =========================
// generate cases
// =========================

function generateCases(canonicalUrl) {
  const expectedUrl = normalizeUrl(canonicalUrl);

  return [
    { caseName: "http", testUrl: toHttp(expectedUrl), expectedUrl },
    { caseName: "http_slash", testUrl: addTrailingSlash(toHttp(expectedUrl)), expectedUrl },
    { caseName: "http_www", testUrl: addWww(toHttp(expectedUrl)), expectedUrl },
    { caseName: "http_www_slash", testUrl: addTrailingSlash(addWww(toHttp(expectedUrl))), expectedUrl },
    { caseName: "https_www", testUrl: addWww(expectedUrl), expectedUrl },
    { caseName: "https_www_slash", testUrl: addTrailingSlash(addWww(expectedUrl)), expectedUrl },
    { caseName: "slash", testUrl: addTrailingSlash(expectedUrl), expectedUrl },
    { caseName: "uppercase", testUrl: uppercasePath(expectedUrl), expectedUrl },
    { caseName: "underscore", testUrl: replaceHyphenWithUnderscore(expectedUrl), expectedUrl },
    { caseName: "percent20", testUrl: replaceHyphenWithPercent20(expectedUrl), expectedUrl }
  ];
}

// =========================
// http
// =========================

async function fetchWithTimeout(url, timeoutMs) {
  return fetch(url, {
    method: "GET",
    redirect: "manual",
    signal: AbortSignal.timeout(timeoutMs)
  });
}

async function followRedirects(url, maxRedirects = 10, timeoutMs = 30000) {
  let current = url;
  let redirectCount = 0;
  let lastStatus = null;
  const chain = [];

  while (redirectCount <= maxRedirects) {
    const response = await fetchWithTimeout(current, timeoutMs);

    lastStatus = response.status;
    const locationHeader = response.headers.get("location");

    chain.push({
      url: current,
      status: lastStatus,
      location: locationHeader || ""
    });

    if (![301, 302, 307, 308].includes(lastStatus)) {
      return {
        finalUrl: current,
        redirectCount,
        lastStatus,
        chain
      };
    }

    if (!locationHeader) {
      return {
        finalUrl: current,
        redirectCount,
        lastStatus,
        chain
      };
    }

    current = new URL(locationHeader, current).toString();
    redirectCount++;
  }

  return {
    finalUrl: current,
    redirectCount,
    lastStatus,
    chain
  };
}

// =========================
// main
// =========================

async function main() {
  const allCases = canonicalUrls.flatMap(generateCases);
  const results = [];

  console.log(`Canonical URLs: ${canonicalUrls.length}`);
  console.log(`Generated test cases: ${allCases.length}`);
  console.log("");

  let index = 0;

  const strictSlashCases = [
    "slash",
    "http_slash",
    "http_www_slash",
    "https_www_slash"
  ];

  for (const testCase of allCases) {
    index++;
    console.log(`[${index}/${allCases.length}] ${testCase.caseName} -> ${testCase.testUrl}`);

    try {
      const redirectInfo = await followRedirects(testCase.testUrl, 10, 30000);

      const finalRaw = redirectInfo.finalUrl;
      const finalNormalized = normalizeUrl(redirectInfo.finalUrl);
      const expected = testCase.expectedUrl;

      let pass = false;
      let note = "";

      if (strictSlashCases.includes(testCase.caseName)) {
        const isLangRoot = isLanguageRootUrl(expected);

        if (isLangRoot) {
          pass =
            redirectInfo.redirectCount > 0 &&
            finalNormalized === expected;

          if (!pass) {
            if (redirectInfo.redirectCount === 0) {
              note = "No redirect happened";
            } else {
              note = "Final URL mismatch";
            }
          }
        } else {
          pass =
            redirectInfo.redirectCount > 0 &&
            finalRaw === expected;

          if (!pass) {
            if (redirectInfo.redirectCount === 0) {
              note = "No redirect happened";
            } else {
              note = "Trailing slash was not removed";
            }
          }
        }
      } else {
        pass =
          redirectInfo.redirectCount > 0 &&
          finalNormalized === expected;

        if (!pass) {
          if (redirectInfo.redirectCount === 0) {
            note = "No redirect happened";
          } else {
            note = "Final URL mismatch";
          }
        }
      }

      results.push({
        result: pass ? "PASS" : "FAIL",
        caseName: testCase.caseName,
        testUrl: testCase.testUrl,
        expectedUrl: expected,
        finalUrl: finalRaw,
        normalizedFinalUrl: finalNormalized,
        redirectCount: redirectInfo.redirectCount,
        lastStatus: redirectInfo.lastStatus,
        chain: redirectInfo.chain
          .map(step => `${step.status}:${step.url}${step.location ? ` -> ${step.location}` : ""}`)
          .join(" | "),
        note
      });
    } catch (error) {
      console.log(`ERROR -> ${testCase.testUrl}: ${error.message}`);

      results.push({
        result: "ERROR",
        caseName: testCase.caseName,
        testUrl: testCase.testUrl,
        expectedUrl: testCase.expectedUrl,
        finalUrl: "",
        normalizedFinalUrl: "",
        redirectCount: "",
        lastStatus: "",
        chain: "",
        note: error.message
      });
    }
  }

  const headers = [
    "result",
    "caseName",
    "testUrl",
    "expectedUrl",
    "finalUrl",
    "normalizedFinalUrl",
    "redirectCount",
    "lastStatus",
    "chain",
    "note"
  ];

  const csvLines = [
    headers.join(","),
    ...results.map(row => headers.map(h => csvEscape(row[h])).join(","))
  ];

  fs.writeFileSync("redirect_report_new-category.csv", csvLines.join("\n"), "utf8");

  const passed = results.filter(r => r.result === "PASS").length;
  const failed = results.filter(r => r.result === "FAIL").length;
  const errored = results.filter(r => r.result === "ERROR").length;

  console.log("");
  console.log("Done.");
  console.log(`PASS: ${passed}`);
  console.log(`FAIL: ${failed}`);
  console.log(`ERROR: ${errored}`);
  console.log("Report saved to redirect_report_new-category.csv");
}

main();