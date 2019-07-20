# Sponsor Tool
The purpose of this project is to automatically collect, identify, and send emails to companies that could potentially sponsor the Olin Electric Motorsports Team.

## Structure
* Search guidelines
  * Keyword queries
  * blacklist companies/urls
  * Returns list of URLs
* Website Crawler
  * get all links of website, make a graph
  * Harvest all emails
  * Try to figure out company values based on text
  * Determine company name
  * Search google for company value
  * Search wikipedia for company summary
  * Search google for company distance to Olin
* Database
  * store all websites and company information
* Emailer
  * #sendit
