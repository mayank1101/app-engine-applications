#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__),"templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape = True)


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        self.render('applications.html')


lower_case = [chr(x) for x in range(97, 123)]
upper_case = [chr(x) for x in range(65, 91)]


def decryption(c, letterStr):
    result = ""
    actual_index = letterStr.index(c)
    loc = actual_index - 13
    if loc < 0:
        loc = (ord(letterStr[25]) - (ord(letterStr[abs(loc) - 1])))
        result += letterStr[loc]
    else:
        result += letterStr[loc]
    return result


# A simple rot13 Application
class RotHandler(Handler):
    def get(self):
        self.render('rot13.html')

    def post(self):
        if self.request.get('submit') == 'e':
            text = self.request.get('data_enc')
            rot13 = ''
            rot13 = text.encode('rot13')
            self.render('rot13.html', enc_data=rot13)
        elif self.request.get('submit') == 'd':
            text = self.request.get('data_dec')
            decrypt = " "
            for i in range(len(text)):
                if text[i].isupper():
                    decrypt += decryption(text[i], upper_case)
                    print "inside if" + decrypt
                elif text[i].islower():
                    decrypt += decryption(text[i], lower_case)
                    print "inside elif" + decrypt
                else:
                    decrypt += text[i]
            self.render('rot13.html', dec_data=decrypt)


# A simple ASCII Art app
class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created_time = db.DateTimeProperty(auto_now_add = True)


class ArtHandler(Handler):
    def render_art(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created_time DESC")

        self.render('asciiArt.html',title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_art()

    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')

        if title and art:
            a = Art(title=title, art=art)
            a.put()
            self.redirect('/asciiArt')
        else:
            error = "Both title and art is needed!"
            self.render_art(title, art, error)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/rot13', RotHandler),
                               ('/asciiArt',ArtHandler)
                               ], debug=True)
