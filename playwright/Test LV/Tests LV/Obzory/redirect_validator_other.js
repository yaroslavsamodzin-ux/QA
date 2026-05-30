const fs = require("fs");

const canonicalUrls = [
  "https://test.automoto.com.lv/lv",
  "https://test.automoto.com.lv/lv/auto-zinas",
  "https://test.automoto.com.lv/lv/auto-apskati",
  "https://test.automoto.com.lv/lv/auto-apskati/audi",
  "https://test.automoto.com.lv/lv/auto-apskati/audi/2020",
  "https://test.automoto.com.lv/lv/auto-apskati/audi/a3",
  "https://test.automoto.com.lv/lv/auto-apskati/2020",
  "https://test.automoto.com.lv/lv/auto-apskati/sedans",
  "https://test.automoto.com.lv/lv/auto-dileri",
  "https://test.automoto.com.lv/lv/auto-dileri/audi",
  "https://test.automoto.com.lv/lv/auto-dileri/latvija",
  "https://test.automoto.com.lv/lv/auto-dileri/latvija/ogres-novads",
  "https://test.automoto.com.lv/lv/auto-dileri/latvija/ogre",
  "https://test.automoto.com.lv/lv/auto-dileri/latvija/audi",
  "https://test.automoto.com.lv/lv/about",
  "https://test.automoto.com.lv/lv/contact",
  "https://test.automoto.com.lv/lv/advertising",
  "https://test.automoto.com.lv/lv/info-pages",
  "https://test.automoto.com.lv/lv/privacy",
  "https://test.automoto.com.lv/lv/terms",
  "https://test.automoto.com.lv/lv/refund",
  "https://test.automoto.com.lv/ru",
  "https://test.automoto.com.lv/ru/avto-novosti",
  "https://test.automoto.com.lv/ru/obzory-avto",
  "https://test.automoto.com.lv/ru/obzory-avto/audi",
  "https://test.automoto.com.lv/ru/obzory-avto/audi/2020",
  "https://test.automoto.com.lv/ru/obzory-avto/audi/a3",
  "https://test.automoto.com.lv/ru/obzory-avto/2020",
  "https://test.automoto.com.lv/ru/obzory-avto/sedan",
  "https://test.automoto.com.lv/ru/avtosalony",
  "https://test.automoto.com.lv/ru/avtosalony/audi",
  "https://test.automoto.com.lv/ru/avtosalony/latviya",
  "https://test.automoto.com.lv/ru/avtosalony/latviya/ogrskiy-kray",
  "https://test.automoto.com.lv/ru/avtosalony/latviya/ogre",
  "https://test.automoto.com.lv/ru/avtosalony/latviya/audi",
  "https://test.automoto.com.lv/ru/about",
  "https://test.automoto.com.lv/ru/contact",
  "https://test.automoto.com.lv/ru/advertising",
  "https://test.automoto.com.lv/ru/info-pages",
  "https://test.automoto.com.lv/ru/privacy",
  "https://test.automoto.com.lv/ru/terms",
  "https://test.automoto.com.lv/ru/refund",
  "https://test.automoto.com.lv/en",
  "https://test.automoto.com.lv/en/auto-news",
  "https://test.automoto.com.lv/en/cars-overviews",
  "https://test.automoto.com.lv/en/cars-overviews/audi",
  "https://test.automoto.com.lv/en/cars-overviews/audi/2020",
  "https://test.automoto.com.lv/en/cars-overviews/audi/a3",
  "https://test.automoto.com.lv/en/cars-overviews/2020",
  "https://test.automoto.com.lv/en/cars-overviews/sedan",
  "https://test.automoto.com.lv/en/car-dealerships",
  "https://test.automoto.com.lv/en/car-dealerships/audi",
  "https://test.automoto.com.lv/en/car-dealerships/latvia",
  "https://test.automoto.com.lv/en/car-dealerships/latvia/ogre-municipality",
  "https://test.automoto.com.lv/en/car-dealerships/latvia/ogre",
  "https://test.automoto.com.lv/en/car-dealerships/latvia/audi",
  "https://test.automoto.com.lv/en/about",
  "https://test.automoto.com.lv/en/contact",
  "https://test.automoto.com.lv/en/advertising",
  "https://test.automoto.com.lv/en/info-pages",
  "https://test.automoto.com.lv/en/privacy",
  "https://test.automoto.com.lv/en/terms",
  "https://test.automoto.com.lv/en/refund"
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

  fs.writeFileSync("redirect_report_other.csv", csvLines.join("\n"), "utf8");

  const passed = results.filter(r => r.result === "PASS").length;
  const failed = results.filter(r => r.result === "FAIL").length;
  const errored = results.filter(r => r.result === "ERROR").length;

  console.log("");
  console.log("Done.");
  console.log(`PASS: ${passed}`);
  console.log(`FAIL: ${failed}`);
  console.log(`ERROR: ${errored}`);
  console.log("Report saved to redirect_report_other.csv");
}

main();