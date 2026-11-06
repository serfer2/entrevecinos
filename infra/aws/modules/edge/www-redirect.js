// CloudFront Function (viewer request): www.${domain}/<ruta>?<query> → 301 a https://${domain}/<ruta>?<query>.
function handler(event) {
  var request = event.request;
  var host = request.headers.host ? request.headers.host.value : "";

  if (host.toLowerCase() !== "www.${domain}") {
    return request;
  }

  var pairs = [];
  var query = request.querystring;
  for (var key in query) {
    var values = query[key].multiValue || [query[key]];
    for (var i = 0; i < values.length; i++) {
      pairs.push(values[i].value === "" ? key : key + "=" + values[i].value);
    }
  }
  var location = "https://${domain}" + request.uri + (pairs.length ? "?" + pairs.join("&") : "");

  return {
    statusCode: 301,
    statusDescription: "Moved Permanently",
    headers: { location: { value: location } },
  };
}
