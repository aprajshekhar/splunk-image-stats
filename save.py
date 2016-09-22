import pycurl
from StringIO import StringIO


def save_data(data_json, cert_path, cert_passphrase, url, save_entity, version):
    save_url = url+'rest/data/insert/'+save_entity+'/'+version
    curl = pycurl.Curl()
    curl.setopt(pycurl.SSL_VERIFYPEER, 0)
    curl.setopt(pycurl.SSL_VERIFYHOST, 0)
    curl.setopt(pycurl.VERBOSE, True)
    curl.setopt(pycurl.URL, save_url)
    curl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
    curl.setopt(pycurl.CUSTOMREQUEST, "PUT")
    curl.setopt(pycurl.POSTFIELDS, data_json)
    curl.setopt(pycurl.SSLKEYTYPE, "PEM")
    curl.setopt(pycurl.SSLKEY, cert_path)
    curl.setopt(pycurl.SSLKEYPASSWD, cert_passphrase)
    buff = StringIO()
    curl.setopt(pycurl.WRITEFUNCTION, buff.write)

    curl.perform()
    return buff.getvalue()

