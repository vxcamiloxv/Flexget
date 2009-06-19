import re, urllib2, logging
from flexget.plugins.module_resolver import ResolverException
from flexget.plugin import *
from flexget.utils.soup import get_soup

log = logging.getLogger('google_cse')

class ResolveGoogleCse:
    """Google custom query resolver."""

    # resolver API
    def resolvable(self, feed, entry):
        if entry['url'].startswith('http://www.google.com/cse?'): return True
        if entry['url'].startswith('http://www.google.com/custom?'): return True
        return False
        
    # resolver API
    def resolve(self, feed, entry):
        try:
            # need to fake user agent
            txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
            req = urllib2.Request(entry['url'], None, txheaders)
            page = urllib2.urlopen(req)
            soup = get_soup(page)
            results = soup.findAll('a', attrs={'class': 'l'})
            if not results:
                raise ResolverException('No results')
            for res in results:
                url = res.get('href')
                url = url.replace('/interstitial?url=', '')
                # generate match regexp from google search result title
                regexp = '.*'.join([x.contents[0] for x in res.findAll('em')])
                if re.match(regexp, entry['title']):
                    log.debug('resolved, found with %s' % regexp)
                    entry['url'] = url
                    return
            raise ResolverException('Unable to resolve')
        except Exception, e:
            raise ResolverException(e)

register_plugin(ResolveGoogleCse, 'google_cse', groups=['resolver'])
