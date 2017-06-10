from flask import request, redirect, flash, url_for
from pprint import pformat
from main import *
import validators


@app.route("/<short_url>", methods=['GET', 'POST'])
def retrieve(short_url):
    if short_url is None or short_url == 'favicon.ico':
        return redirect(url_for("index"))

    if short_url_exists(short_url):
        shortening = get_shortening(short_url=short_url)
        shortening += 1

        return redirect(shortening.long_url, code=302)
    else:
        flash('{} is not mapped to any URL.'.format(
            request.url_root + short_url))
        return redirect(url_for("index"))


@app.route("/", methods=['GET', 'POST'])
def index():
    data = {
        'number_of_urls': get_number_of_shortenings(),
        'remote_address': get_remote_address(),
        'debug': app.config['DEBUG'],
    }

    if request.method == 'POST':
        protocol = request.form['protocol']
        long_url_without_protocol = request.form['url']
        long_url = protocol + long_url_without_protocol
        base_url = request.url_root

        if not validators.url(long_url, public=True):
            flash("%s is not a valid URL." % long_url)
            print("%s is not a valid URL." % long_url)
            return redirect(url_for('index'))

        if not long_url_exists(long_url):
            try:
                shorten(long_url)
            except Exception as e:
                return 'could not shorten <samp>%s</samp>: %s' % (long_url, e)

        data.update({
            'protocol': protocol,
            'long_url_without_protocol': long_url_without_protocol,
            'long_url': long_url,
            'short_url': get_short_url(long_url),
            'base_url': base_url,
        })

    pretty_data = pformat(data, indent=2).replace("\n", "<br>")
    print(pretty_data)

    return render_template("index.html", data=data, pretty_data=pretty_data)


@app.route("/all")
def show_all():
    return render_template("all.html",
                           shortenings=get_all_shortenings(),
                           url_root=request.url_root)


@app.errorhandler(404)
def page_not_found(error):
    return "page not found"
