import copy
import gc
import time
from werkzeug.serving import ThreadedWSGIServer
from easy_utils_dev.utils import getRandomKey , generateToken , getTimestamp
from flask_socketio import SocketIO
from engineio.async_drivers import gevent
from flask_cors import CORS
import logging  , os
from flask import jsonify, request , current_app
from flask import Flask
from threading import Thread
import threading
from easy_utils_dev.custom_env import cenv
from easy_utils_dev.utils import kill_thread
from multiprocessing import Process
from werkzeug.serving import make_ssl_devcert
from time import sleep
from easy_utils_dev.utils import start_thread , getRandomKeysAndStr , mkdirs
from easy_utils_dev.temp_memory import TemporaryMemory

def getClassById( id ) :
    return cenv[id]

def create_ssl(host,output) :
    '''
    host : is the IP/Adress of the server which servers the web-server
    output: the output locaiton to generate the ssl certificate. it should end with filename without extension
    '''
    return make_ssl_devcert( output , host=host)

def clone_request(request):
    """Return a plain dict clone of Flask request data."""
    return {
        "method": request.method,
        "path": request.path,
        "url": request.url,
        "headers": dict(request.headers),
        "args": request.args.to_dict(flat=False),
        "form": request.form.to_dict(flat=False),
        "json": request.get_json(silent=True),
        "data": request.get_data(),   # raw body bytes
        "files": {k: v.filename for k, v in request.files.items()},
        "remote_addr": request.remote_addr,
        "cookies": request.cookies,
    }

class AbortRequest :
    def __init__(self, request ) :
        self.request = clone_request(request)
        self.abort_id = None
        self.abortable = False
        self.thread = None
        self.cache = None
        self.start_ts = getTimestamp()

    def abort(self) : 
        kill_thread(self.thread)
        self.cache.delete(self.abort_id)
        try :
            gc.collect()
        except :
            pass


class UISERVER :
    def __init__(self ,
            id=getRandomKey(n=15),
            secretkey=generateToken(),
            address='localhost',
            port=5312 , 
            https=False , 
            ssl_crt=None,
            ssl_key=None,
            template_folder='templates/' ,
            static_folder = 'templates/assets'
            ,**kwargs
        ) -> None:
        self.id = id
        self.static_folder = static_folder
        self.app = app = Flask(self.id , template_folder=template_folder  ,  static_folder=self.static_folder )
        app.config['SECRET_KEY'] = secretkey
        CORS(app,resources={r"/*":{"origins":"*"}})
        self.address= address 
        self.port = port
        self.thread = None
        self.ssl_crt=ssl_crt
        self.ssl_key=ssl_key
        self.enable_test_url=True
        self.abort_requests = {}
        self.abort_base_url = '/request/abort'
        if https :
            self.httpProtocol = 'https'
        else :
            self.httpProtocol = 'http'
        self.socketio = SocketIO(app , cors_allowed_origins="*"  ,async_mode='threading' , engineio_logger=False , always_connect=True ,**kwargs )
        cenv[id] = self
        self.fullAddress = f"{self.httpProtocol}://{self.address}:{self.port}"
        self.cache = TemporaryMemory()

    def update_cert(self , crt, ssl ) :
        self.ssl_crt=crt
        self.ssl_key=ssl

    def register_abortable_request(self , request , abort_id = None ) :
        path = request.path
        Abort = AbortRequest(request)
        if not path.startswith(self.abort_base_url) :
            if not abort_id :
                if not request.headers.get('abortid') :
                    abort_id = getRandomKeysAndStr(n=20)
                else :
                    abort_id = request.headers.get('abortid')
            
            Abort.abort_id = abort_id
            current_thread = threading.current_thread()
            Abort.thread = current_thread
            Abort.cache = self.cache
            Abort.start_ts = getTimestamp()
            self.cache.set( Abort , custom_key=abort_id , auto_destroy_period=120 , store_deleted_key=False )
        return Abort

    def start_before_request(self) : 

        @self.app.route(f'{self.abort_base_url}/<id>' , methods=['DELETE'])
        def abort_request(id : str ) :
            abort : AbortRequest = self.cache.get(id)
            timestamp = getTimestamp()
            if abort :
                abort.abort()
                for i in range(30) :
                    th = abort.thread
                    alive = th.is_alive()
                    if not alive :
                        break
                    time.sleep(.25)
                return { 'status' : 200 , 'message' : 'Request aborted' , 'abort_timestamp' : timestamp , 'abort_id' : id , 'alive' : alive  , 'url' : abort.request.get('path')}
            else :
                return { 'status' : 404 , 'message' : 'Request not found or request is not abortable. Check request headers for abortable flag.'}

        @self.app.before_request
        def before_request() :
            abortable = request.headers.get('abortable')
            if abortable :
                abort = self.register_abortable_request(request)
                request.abortable = True
                request.abort_id = abort.abort_id
                # check here if async in the headers
                # if yes . i will trigger the function in thread 
                # start_tread(#how to get the target function here ? )
                # now i want to return response to UI { status : 200 , message : 'request now in running bg' , abort_id : abort.abort_id }
                # the flask function should not be called again
                if request.headers.get('async') == 'false' : 
                    target_func = current_app.view_functions.get(request.endpoint)
                    if not target_func:
                        return jsonify({"error": "Route not found"}), 404
                    th = start_thread(target=target_func, args=request.args, kwargs=request.form)
                    abort.thread = th
                    return {"status": 200, "message": "Request now in running bg", "abort_id": abort.abort_id} , 200

        @self.app.after_request
        def after_request(response) :
            try :
                if request.abortable :
                    response.headers['abortid'] = request.abort_id 
                    response.headers['abortable'] = True
            except :
                response.headers['abortable'] = False
            return response


    def getInstance(self) :
        return self.getFlask() , self.getSocketio() , self.getWsgi()
    
    def getSocketio( self ):
        return self.socketio
    
    def getFlask( self ):
        return self.app
    
    def getWsgi(self) :
        return self.wsgi_server
    
    def shutdownUi(self) :
        kill_thread(self.thread)
        self.wsgi_server.server_close()
        self.wsgi_server.shutdown()

    def _wait_th(self , t ) :
        t.join()
        
    def thrStartUi(self , suppress_prints=True) :
        if self.enable_test_url :
            if not suppress_prints :
                print(f'TEST URL GET-METHOD /connection/test/internal')
            @self.app.route('/connection/test/internal' , methods=['GET'])
            def test_connection():
                return f"Status=200<br> ID={self.id}<br> one-time-token={getRandomKey(20)}"
        if self.httpProtocol == 'http' :
            con = None
        elif self.httpProtocol == 'https' :
            con=(self.ssl_crt , self.ssl_key)
        self.wsgi_server = wsgi_server = ThreadedWSGIServer(
            host = self.address ,
            ssl_context=con,
            # ssl_context=('ssl.crt', 'ssl.key'),
            port = self.port,
            app = self.app )
        if not suppress_prints :
            print(f"web-socket: {self.fullAddress}")
            print(f"UI URL : {self.fullAddress}")
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        wsgi_server.serve_forever()
    
    def startUi(self ,daemon , suppress_prints=True) :
        self.start_before_request()
        self.thread = self.flaskprocess = Thread(target=self.thrStartUi , args=[suppress_prints])
        self.flaskprocess.daemon = False
        self.flaskprocess.start()
        start_thread(target=self._wait_th , args=[self.thread] , daemon=daemon)
        return self.thread
    
    def stopUi(self) :
        kill_thread(self.thread)
        return True
    
