#!/usr/bin/env python
import datetime
import random
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

class PageView(db.Model):
  url = db.TextProperty()
  referrer = db.TextProperty()
  session_id = db.StringProperty()
  ip_address = db.StringProperty()
  created_at = db.DateTimeProperty(auto_now_add=True)
  user_id = db.IntegerProperty()


class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>Hello world!<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js" type="text/javascript"></script><script>function trackPageView(url) {'+'$.post(\'/pageviews.json\', {u: url, referrer: document.referrer}, function(data) {'+'if (data[\'status\'] == \'error\') { alert(data.toString()); }' + '});'+ '}'+'trackPageView(window.location.href);</script></body></html>')

class PageViewsHandler(webapp.RequestHandler):
  def post(self):
    if '_pvk' not in self.request.cookies or (self.request.cookies['_pvk'] == None or self.request.cookies['_pvk'] == ''):
      self.request.cookies['_pvk'] = str(datetime.datetime.utcnow()) + '-' + str(random.getrandbits(50))
      # self.response.set_cookie('_pvk', str(datetime.utcnow()) + '-' + str(random.getrandbits(50)), max_age=360000000)

    page_view = PageView()

    if False: # change this to somehow get the user id
      page_view.user_id = get_current_user().id

    page_view.url = self.request.get('u')
    page_view.referrer = self.request.get('referrer')
    page_view.session_id = self.request.cookies['_pvk']
    page_view.ip_address = self.request.remote_addr
    page_view.put()
    
    self.response.out.write('{status: \'ok\'}')

class AdminPageViewsHandler(webapp.RequestHandler):
  def get(self):
    page_views = db.GqlQuery("SELECT * FROM PageView ORDER BY created_at DESC")
    result = ''
    for page_view in page_views:
      result += "<tr><td>"+page_view.url+"</td><td>"+page_view.referrer+"</td><td>"+page_view.session_id+"</td><td>"+page_view.ip_address+"</td><td>"+str(page_view.created_at)+"</td><td>"+str(page_view.user_id)+"</td></tr>"
    
    self.response.out.write('<html><body>Page Views:<table><tr><td>URL</td><td>Referrer</td><td>Session ID</td><td>IP Address</td><td>Created At</td><td>User ID</td></tr>'+result+'</table></body></html>')


def main():
  application = webapp.WSGIApplication([('/', MainHandler), ('/pageviews.json', PageViewsHandler), ('/admin/pageviews', AdminPageViewsHandler)], debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
