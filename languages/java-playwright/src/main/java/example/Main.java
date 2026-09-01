package example;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.CDPSession;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Map;

public final class Main {
  public static void main(String[] args) throws Exception {
    String endpoint = "https://browser.zyte.com";
    String apiKey = System.getenv("ZYTE_API_KEY");
    if (apiKey == null || apiKey.isEmpty()) {
      throw new IllegalStateException("ZYTE_API_KEY is required");
    }

    String authorization = "Basic " + Base64.getEncoder()
        .encodeToString((apiKey + ":").getBytes(StandardCharsets.UTF_8));
    Map<String, String> headers = Map.of("Authorization", authorization);
    HttpClient client = HttpClient.newHttpClient();
    URI discoveryUri = URI.create(endpoint + "/json/version");
    HttpResponse<String> response = null;
    for (int redirects = 0; redirects < 5; redirects++) {
      HttpRequest request = HttpRequest.newBuilder(discoveryUri)
          .header("Authorization", authorization)
          .build();
      response = client.send(request, HttpResponse.BodyHandlers.ofString());
      if (response.statusCode() < 300 || response.statusCode() >= 400) {
        break;
      }

      String location = response.headers().firstValue("location")
          .orElseThrow(() -> new IllegalStateException("CDP discovery redirect has no location"));
      discoveryUri = discoveryUri.resolve(location);
      String host = discoveryUri.getHost();
      if (!"https".equals(discoveryUri.getScheme()) || host == null
          || !(host.equals("browser.zyte.com") || host.endsWith(".browser.zyte.com"))) {
        throw new IllegalStateException("CDP discovery refused an untrusted redirect");
      }
    }
    if (response == null) {
      throw new IllegalStateException("CDP discovery did not return a response");
    }
    if (response.statusCode() / 100 != 2) {
      throw new IllegalStateException("CDP discovery failed with HTTP " + response.statusCode());
    }

    JsonObject discovery = JsonParser.parseString(response.body()).getAsJsonObject();
    if (!discovery.has("webSocketDebuggerUrl")) {
      throw new IllegalStateException("CDP discovery response has no webSocketDebuggerUrl");
    }
    String websocketUrl = discovery.get("webSocketDebuggerUrl").getAsString();

    Playwright.CreateOptions playwrightOptions = new Playwright.CreateOptions()
        .setEnv(Map.of("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", "1"));
    try (Playwright playwright = Playwright.create(playwrightOptions)) {
      Browser browser = playwright.chromium().connectOverCDP(
          websocketUrl,
          new BrowserType.ConnectOverCDPOptions().setHeaders(headers));
      CDPSession browserSession = browser.newBrowserCDPSession();
      try {
        if (browser.contexts().isEmpty()) {
          throw new IllegalStateException("The CDP browser has no default context");
        }
        BrowserContext context = browser.contexts().get(0);
        Page page = context.newPage();
        page.navigate("https://quotes.toscrape.com/js/");
        page.waitForSelector(".quote");

        System.out.println("Title: " + page.title());
        System.out.println("Quotes: " + page.locator(".quote").count());

        CDPSession cdp = context.newCDPSession(page);
        JsonObject version = cdp.send("Browser.getVersion");
        System.out.println("Browser: " + version.get("product").getAsString());
        cdp.detach();
        page.close();
      } finally {
        if (browser.isConnected()) {
          browserSession.send("Browser.close");
        }
      }
    }
  }
}
