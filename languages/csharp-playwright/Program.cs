using System.Text;
using System.Text.Json;
using Microsoft.Playwright;

string endpoint = "https://browser.zyte.com";
string? apiKey = Environment.GetEnvironmentVariable("ZYTE_API_KEY");
if (string.IsNullOrEmpty(apiKey))
{
    throw new InvalidOperationException("ZYTE_API_KEY is required");
}

string authorization = "Basic " + Convert.ToBase64String(Encoding.UTF8.GetBytes(apiKey + ":"));

using HttpClientHandler handler = new() { AllowAutoRedirect = false };
using HttpClient httpClient = new(handler) { Timeout = TimeSpan.FromSeconds(120) };

Uri discoveryUri = new(endpoint + "/json/version");
HttpResponseMessage response;
for (int redirects = 0; ; redirects++)
{
    using HttpRequestMessage request = new(HttpMethod.Get, discoveryUri);
    request.Headers.Add("Authorization", authorization);
    response = await httpClient.SendAsync(request);
    if ((int)response.StatusCode < 300 || (int)response.StatusCode >= 400)
    {
        break;
    }

    if (redirects == 4)
    {
        response.Dispose();
        throw new InvalidOperationException("CDP discovery exceeded the redirect limit");
    }

    string location = response.Headers.Location?.OriginalString
        ?? throw new InvalidOperationException("CDP discovery redirect has no location");
    response.Dispose();
    discoveryUri = new Uri(discoveryUri, location);
    bool trustedHost = discoveryUri.Host.Equals("browser.zyte.com", StringComparison.OrdinalIgnoreCase)
        || discoveryUri.Host.EndsWith(".browser.zyte.com", StringComparison.OrdinalIgnoreCase);
    if (discoveryUri.Scheme != "https" || !trustedHost)
    {
        throw new InvalidOperationException("CDP discovery refused an untrusted redirect");
    }
}

string body;
using (response)
{
    if ((int)response.StatusCode / 100 != 2)
    {
        throw new HttpRequestException($"CDP discovery failed with HTTP {(int)response.StatusCode}");
    }
    body = await response.Content.ReadAsStringAsync();
}

using JsonDocument document = JsonDocument.Parse(body);
if (!document.RootElement.TryGetProperty("webSocketDebuggerUrl", out JsonElement wsElement))
{
    throw new InvalidOperationException("CDP discovery response has no webSocketDebuggerUrl");
}
string websocketUrl = wsElement.GetString()
    ?? throw new InvalidOperationException("CDP discovery webSocketDebuggerUrl is not a string");

IPlaywright playwright = await Playwright.CreateAsync();
IBrowser browser = await playwright.Chromium.ConnectOverCDPAsync(
    websocketUrl,
    new BrowserTypeConnectOverCDPOptions
    {
        Headers = new Dictionary<string, string>
        {
            ["Authorization"] = authorization,
        },
    });
ICDPSession browserSession = await browser.NewBrowserCDPSessionAsync();
try
{
    if (browser.Contexts.Count == 0)
    {
        throw new InvalidOperationException("The CDP browser has no default context");
    }
    IBrowserContext context = browser.Contexts[0];
    IPage page = await context.NewPageAsync();
    await page.GotoAsync("https://quotes.toscrape.com/js/");
    await page.WaitForSelectorAsync(".quote");

    Console.WriteLine($"Title: {await page.TitleAsync()}");
    Console.WriteLine($"Quotes: {await page.Locator(".quote").CountAsync()}");

    ICDPSession cdpSession = await context.NewCDPSessionAsync(page);
    JsonElement? version = await cdpSession.SendAsync("Browser.getVersion");
    Console.WriteLine($"Browser: {version?.GetProperty("product").GetString()}");
    await cdpSession.DetachAsync();
    await page.CloseAsync();
}
finally
{
    if (browser.IsConnected)
    {
        await browserSession.SendAsync("Browser.close");
    }
    playwright.Dispose();
}
