const fs = require("fs");

const canonicalUrls = [
"https://automoto.com.lv/lv/lietoti-auto/latvija",
"https://automoto.com.lv/lv/lietoti-auto/latvija/2012",
"https://automoto.com.lv/lv/lietoti-auto/latvija/sedans",
"https://automoto.com.lv/lv/lietoti-auto/latvija/automatiska",
"https://automoto.com.lv/lv/lietoti-auto/latvija/dizelis",
"https://automoto.com.lv/lv/lietoti-auto/latvija/priekseja-piedzina",
"https://automoto.com.lv/lv/lietoti-auto/latvija/zils",
"https://automoto.com.lv/lv/lietoti-auto/latvija/1.6",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/2012",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/sedans",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/automatiska",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/dizelis",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/priekseja-piedzina",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/zils",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/1.6",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/2012",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/sedans",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/automatiska",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/dizelis",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/priekseja-piedzina",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/zils",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/1.6",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/1.6/automatiska",
"https://automoto.com.lv/lv/lietoti-auto/latvija/audi/a3/dizelis/automatiska",
"https://automoto.com.lv/lv/lietoti-auto/latvija/riga",
"https://automoto.com.lv/lv/lietoti-auto/latvija/riga/audi",
"https://automoto.com.lv/lv/lietoti-auto/latvija/riga/sedans",
"https://automoto.com.lv/lv/lietoti-auto/latvija/riga/audi/a3",
"https://automoto.com.lv/lv/lietoti-auto/latvija/riga/audi/sedans",
"https://automoto.com.lv/lv/lietoti-auto/latvija/riga/audi/a3/2012",
"https://automoto.com.lv/lv/lietoti-auto/latvija/ogres-novads",
"https://automoto.com.lv/ru/bu-avto",
"https://automoto.com.lv/ru/bu-avto/latviya/2012",
"https://automoto.com.lv/ru/bu-avto/latviya/sedan",
"https://automoto.com.lv/ru/bu-avto/latviya/avtomat",
"https://automoto.com.lv/ru/bu-avto/latviya/dizel",
"https://automoto.com.lv/ru/bu-avto/latviya/peredniy-privod",
"https://automoto.com.lv/ru/bu-avto/latviya/siniy",
"https://automoto.com.lv/ru/bu-avto/latviya/1.6",
"https://automoto.com.lv/ru/bu-avto/latviya/audi",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/2012",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/sedan",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/avtomat",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/dizel",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/peredniy-privod",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/siniy",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/1.6",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/2012",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/sedan",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/avtomat",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/dizel",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/peredniy-privod",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/siniy",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/1.6",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/1.6/avtomat",
"https://automoto.com.lv/ru/bu-avto/latviya/audi/a3/dizel/avtomat",
"https://automoto.com.lv/ru/bu-avto/latviya/riga",
"https://automoto.com.lv/ru/bu-avto/latviya/riga/audi",
"https://automoto.com.lv/ru/bu-avto/latviya/riga/sedan",
"https://automoto.com.lv/ru/bu-avto/latviya/riga/audi/a3",
"https://automoto.com.lv/ru/bu-avto/latviya/riga/audi/sedan",
"https://automoto.com.lv/ru/bu-avto/latviya/riga/audi/a3/2012",
"https://automoto.com.lv/ru/bu-avto/latviya/rizhskiy-rayon",
"https://automoto.com.lv/en/used-cars",
"https://automoto.com.lv/en/used-cars/latvia/2012",
"https://automoto.com.lv/en/used-cars/latvia/sedan",
"https://automoto.com.lv/en/used-cars/latvia/automatic",
"https://automoto.com.lv/en/used-cars/latvia/diesel",
"https://automoto.com.lv/en/used-cars/latvia/front-wheel-drive",
"https://automoto.com.lv/en/used-cars/latvia/blue",
"https://automoto.com.lv/en/used-cars/latvia/1.6",
"https://automoto.com.lv/en/used-cars/latvia/audi",
"https://automoto.com.lv/en/used-cars/latvia/audi/2012",
"https://automoto.com.lv/en/used-cars/latvia/audi/sedan",
"https://automoto.com.lv/en/used-cars/latvia/audi/automatic",
"https://automoto.com.lv/en/used-cars/latvia/audi/diesel",
"https://automoto.com.lv/en/used-cars/latvia/audi/front-wheel-drive",
"https://automoto.com.lv/en/used-cars/latvia/audi/blue",
"https://automoto.com.lv/en/used-cars/latvia/audi/1.6",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/2012",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/sedan",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/automatic",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/diesel",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/front-wheel-drive",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/blue",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/1.6",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/1.6/automatic",
"https://automoto.com.lv/en/used-cars/latvia/audi/a3/diesel/automatic",
"https://automoto.com.lv/en/used-cars/latvia/riga",
"https://automoto.com.lv/en/used-cars/latvia/riga/audi",
"https://automoto.com.lv/en/used-cars/latvia/riga/sedan",
"https://automoto.com.lv/en/used-cars/latvia/riga/audi/a3",
"https://automoto.com.lv/en/used-cars/latvia/riga/audi/sedan",
"https://automoto.com.lv/en/used-cars/latvia/riga/audi/a3/2012",
"https://automoto.com.lv/en/used-cars/latvia/ogre-municipality",
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

  fs.writeFileSync("redirect_report_used-category-country.csv", csvLines.join("\n"), "utf8");

  const passed = results.filter(r => r.result === "PASS").length;
  const failed = results.filter(r => r.result === "FAIL").length;
  const errored = results.filter(r => r.result === "ERROR").length;

  console.log("");
  console.log("Done.");
  console.log(`PASS: ${passed}`);
  console.log(`FAIL: ${failed}`);
  console.log(`ERROR: ${errored}`);
  console.log("Report saved to redirect_report_used-category-country.csv");
}

main();