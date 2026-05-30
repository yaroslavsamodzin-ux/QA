const canonicalUrls = [
"https://test.automoto.com.lv/lv/lietoti-auto",
"https://test.automoto.com.lv/lv/lietoti-auto/2012",
"https://test.automoto.com.lv/lv/lietoti-auto/sedans",
"https://test.automoto.com.lv/lv/lietoti-auto/automatiska",
"https://test.automoto.com.lv/lv/lietoti-auto/dizelis",
"https://test.automoto.com.lv/lv/lietoti-auto/priekseja-piedzina",
"https://test.automoto.com.lv/lv/lietoti-auto/zils",
"https://test.automoto.com.lv/lv/lietoti-auto/1.6",
"https://test.automoto.com.lv/lv/lietoti-auto/audi",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/2012",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/sedans",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/automatiska",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/dizelis",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/priekseja-piedzina",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/zils",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/1.6",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/2012",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/sedans",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/automatiska",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/dizelis",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/priekseja-piedzina",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/zils",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/1.6",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/automatiska/1.6",
"https://test.automoto.com.lv/lv/lietoti-auto/audi/a3/automatiska/dizelis",
];

// Екранування для CSV
function csvEscape(value) {
  const str = String(value ?? "");
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

// Додає slash в кінець path, якщо його нема
function addTrailingSlash(url) {
  const u = new URL(url);
  if (!u.pathname.endsWith("/")) {
    u.pathname += "/";
  }
  return u.toString();
}

// Міняє https -> http
function toHttp(url) {
  const u = new URL(url);
  u.protocol = "http:";
  return u.toString();
}

// Додає www
function addWww(url) {
  const u = new URL(url);
  if (!u.hostname.startsWith("www.")) {
    u.hostname = `www.${u.hostname}`;
  }
  return u.toString();
}

// PATH у верхній регістр
function uppercasePath(url) {
  const u = new URL(url);
  u.pathname = u.pathname.toUpperCase();
  return u.toString();
}

// Замінити дефіси на underscore у path
function replaceHyphenWithUnderscore(url) {
  const u = new URL(url);
  if (!u.pathname.includes("-")) return null;
  u.pathname = u.pathname.replace(/-/g, "_");
  return u.toString();
}

// Замінити дефіси на %20 у path
function replaceHyphenWithPercent20(url) {
  const u = new URL(url);
  if (!u.pathname.includes("-")) return null;
  u.pathname = u.pathname.replace(/-/g, "%20");
  return u.toString();
}

// Прибирає slash у кінці, щоб expectedUrl був canonical
function normalizeExpected(url) {
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

// Генерація тест-кейсів для одного canonical URL
function generateCases(canonicalUrl) {
  const expectedUrl = normalizeExpected(canonicalUrl);

  const cases = [
    {
      caseName: "http",
      testUrl: toHttp(expectedUrl),
      expectedUrl
    },
    {
      caseName: "http_slash",
      testUrl: addTrailingSlash(toHttp(expectedUrl)),
      expectedUrl
    },
    {
      caseName: "http_www",
      testUrl: addWww(toHttp(expectedUrl)),
      expectedUrl
    },
    {
      caseName: "http_www_slash",
      testUrl: addTrailingSlash(addWww(toHttp(expectedUrl))),
      expectedUrl
    },
    {
      caseName: "https_www",
      testUrl: addWww(expectedUrl),
      expectedUrl
    },
    {
      caseName: "https_www_slash",
      testUrl: addTrailingSlash(addWww(expectedUrl)),
      expectedUrl
    },
    {
      caseName: "slash",
      testUrl: addTrailingSlash(expectedUrl),
      expectedUrl
    },
    {
      caseName: "uppercase",
      testUrl: uppercasePath(expectedUrl),
      expectedUrl
    }
  ];

  const underscoreUrl = replaceHyphenWithUnderscore(expectedUrl);
  if (underscoreUrl) {
    cases.push({
      caseName: "underscore",
      testUrl: underscoreUrl,
      expectedUrl
    });
  }

  const percent20Url = replaceHyphenWithPercent20(expectedUrl);
  if (percent20Url) {
    cases.push({
      caseName: "percent20",
      testUrl: percent20Url,
      expectedUrl
    });
  }

  return cases;
}

// Збір усіх кейсів
const allCases = canonicalUrls.flatMap(generateCases);

// Генеруємо CSV
const headers = ["caseName", "testUrl", "expectedUrl"];
const csvRows = [
  headers.join(","),
  ...allCases.map(row =>
    headers.map(header => csvEscape(row[header])).join(",")
  )
];

const csvOutput = csvRows.join("\n");

// Вивід у консоль
console.log(csvOutput);