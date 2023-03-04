// request Axios
const axios = require("axios");
const fs = require("fs");
const scrapingbee = require('scrapingbee');
const more_replies_xpath =
  "//div[@id='contentArea']//a[div/span[contains(text(),'View') and (contains(text(),'more replies') or contains(text(),'more comment'))]]";

var client = new scrapingbee.ScrapingBeeClient('QFPOISA2OZDYCPLXWPJPL0UP4ZE9B999D0F7X7J80X3LGBU2CKSW80HK9KNEI24FA451D46I1QANAV4J');

var  fb_url = "https://www.facebook.com/stephanie.reinke.92/posts/pfbid02Q9rYwrWFvme7e7VRXU1waKewW8VzUDAPCgi6k7q83yFzDsYvYYDpNKfHnn2EBHXl";

async function scrape(url) {
  var response = await client.get({
    url: url,
    // params: {  
    // },
  })
  return response
}

scrape(fb_url)
  .then(function (response) {
      var decoder = new TextDecoder();
      var text = decoder.decode(response.data);
      // console.log(text);
      fs.writeFileSync('results/sample.json', text);
  })
  .catch((e) => console.log('A problem occured : ' + e.response.data));


// axios
//   .get("https://app.scrapingbee.com/api/v1", {
//     params: {
//       api_key:
//         "QFPOISA2OZDYCPLXWPJPL0UP4ZE9B999D0F7X7J80X3LGBU2CKSW80HK9KNEI24FA451D46I1QANAV4J",
//       url: "https://www.facebook.com/stephanie.reinke.92/posts/pfbid02Q9rYwrWFvme7e7VRXU1waKewW8VzUDAPCgi6k7q83yFzDsYvYYDpNKfHnn2EBHXl",


//     //   'js_scenario': {"instructions": [{"click": "form > div > div > button"}, {'wait': '1500' }]} 

//     },

//     // instructions: [
//     //   { wait_for_and_click: "#contentArea" },
//     //   { wait: 250 },
//     // ],
//   })
//   .then(function (response) {
//     // handle success
//     console.log(response);
//     let raw_html = JSON.stringify(response.data).replace('\\\\"', '\\"');

//     fs.writeFileSync("response.html", raw_html, {});
//   })
//   .catch(console.error);
