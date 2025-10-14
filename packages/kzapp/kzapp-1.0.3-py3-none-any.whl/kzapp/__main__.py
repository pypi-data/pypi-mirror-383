import http.server
import email.message
import select
import threading
import time
import platform
import psutil
import socket
import os

appname = 'kzapp'

# -------------------web service--------------------------------

def _start_server(urlhandler, hostname, port):
	'''
	'''

	class DocHandler(http.server.BaseHTTPRequestHandler):

	    def do_GET(self):
	        """Process a request from an HTML browser.

	        The URL received is in self.path.
	        Get an HTML page from self.urlhandler and send it.
	        """
	        if self.path.endswith('.css'):
	            content_type = 'text/css'
	        else:
	            content_type = 'text/html'
	        self.send_response(200)
	        self.send_header('Content-Type', '%s; charset=UTF-8' % content_type)
	        self.end_headers()
	        self.wfile.write(self.urlhandler(
	            self.path, content_type).encode('utf-8'))

	    def log_message(self, *args):
	        # Don't log messages.
	        pass

	class DocServer(http.server.HTTPServer):

	    def __init__(self, host, port, callback):
	        self.host = host
	        self.address = (self.host, port)
	        self.callback = callback
	        self.base.__init__(self, self.address, self.handler)
	        self.quit = False

	    def serve_until_quit(self):
	        while not self.quit:
	            rd, wr, ex = select.select([self.socket.fileno()], [], [], 1)
	            if rd:
	                self.handle_request()
	        self.server_close()

	    def server_activate(self):
	        self.base.server_activate(self)
	        if self.callback:
	            self.callback(self)

	class ServerThread(threading.Thread):

	    def __init__(self, urlhandler, host, port):
	        self.urlhandler = urlhandler
	        self.host = host
	        self.port = int(port)
	        threading.Thread.__init__(self)
	        self.serving = False
	        self.error = None

	    def run(self):
	        """Start the server."""
	        try:
	            DocServer.base = http.server.HTTPServer
	            DocServer.handler = DocHandler
	            DocHandler.MessageClass = email.message.Message
	            DocHandler.urlhandler = staticmethod(self.urlhandler)
	            docsvr = DocServer(self.host, self.port, self.ready)
	            self.docserver = docsvr
	            docsvr.serve_until_quit()
	        except Exception as e:
	            self.error = e

	    def ready(self, server):
	        self.serving = True
	        self.host = server.host
	        self.port = server.server_port
	        self.url = 'http://%s:%d/' % (self.host, self.port)

	    def stop(self):
	        """Stop the server and this thread nicely"""
	        self.docserver.quit = True
	        self.join()
	        # explicitly break a reference cycle: DocServer.callback
	        # has indirectly a reference to ServerThread.
	        self.docserver = None
	        self.serving = False
	        self.url = None

	thread = ServerThread(urlhandler, hostname, port)
	thread.start()
	# Wait until thread.serving is True to make sure we are
	# really up before returning.
	while not thread.error and not thread.serving:
	    time.sleep(.01)
	return thread

def browse(port=0, *, open_browser=False, hostname='localhost', backend=False):
    """Start the enhanced pydoc Web server and open a Web browser.

    Use port '0' to start the server on an arbitrary port.
    Set open_browser to False to suppress opening a browser.
    """
    import webbrowser
    serverthread = _start_server(_url_handler, hostname, port)
    if serverthread.error:
        print(serverthread.error)
        return
    if serverthread.serving:
    	print('Server ready at', serverthread.url)
    	if backend:
    		return

    	server_help_msg = 'Server commands: [b]rowser, [q]uit'
    	if open_browser:
    	    webbrowser.open(serverthread.url)
    	try:
    		print(server_help_msg)
    		while serverthread.serving:
    			cmd = input('server> ')
    			cmd = cmd.lower()
    			if cmd == 'q':
    				break
    			elif cmd == 'b':
    				webbrowser.open(serverthread.url)
    			else:
    				print(server_help_msg)
    	except (KeyboardInterrupt, EOFError):
            print()
    	finally:
        	if serverthread.serving:
        		serverthread.stop()
        		print('Server stopped')

def _url_handler(url, content_type="text/html"):

	css = '''
	<style>
		p, table, tr, td {
			margin: 0;
			font-size: 12px;
		}

		table {
			border-collapse: collapse;
		}

		tr {
			border-bottom: 1px solid rgba(0,0,0, .1);
		}

		td {
			padding-right: 8px;
		}
	</style>
	'''

	info = get_full_info()

	html_platform = ''
	html_usage = ''
	html_network = '''<table>
		<tr>
			<th>IP地址</th>
			<th>IPv6</th>
			<th>mac地址</th>
			<th>子网掩码</th>
			<th>状态</th>
			<th>名称</th>
		</tr>
	'''

	html_disk = '''<table>
		<tr>
			<th>-</th>
			<th>设备</th>
			<th>文件类型</th>
			<th>已用</th>
			<th>全部</th>
			<th>可用</th>
			<th>百分比</th>
		</tr>
	'''

	for _, item in info['platform'].items():
		html_platform += f'<p>{item[1]}: {item[0]}</p>'

	for _, item in info['usage'].items():
		html_usage += f'<p>{item[1]}: {item[0]}</p>'

	for item in info['network']['interfaces']:
		html_network += f'''
			<tr>
				<td>{item.get('ipv4', '')}</td>
				<td>{item.get('ipv6', '')}</td>
				<td>{item.get('mac', '')}</td>
				<td>{item.get('netmask', '')}</td>
				<td>{item.get('isup', '')}</td>
				<td>{item.get('name', '')}</td>
			</tr>
		'''

	for line in info['disk']:
		html_disk += f'''
			<tr>
				<td>{line[0]}</td>
				<td>{line[1]}</td>
				<td>{line[2]}</td>
				<td>{line[3]}</td>
				<td>{line[4]}</td>
				<td>{line[5]}</td>
				<td>{line[6]}</td>
			</tr>
		'''

	html_network += '</table>'
	html_disk += '</table>'

	return f'''
	{css}
	<p>-----------------------系统信息-------------------------</p>
	{html_platform}
	<p>-----------------------网络信息-------------------------</p>
	{html_network}
	<p>-----------------------资源信息-------------------------</p>
	{html_usage}
	{html_disk}
	<p>-----------------------end xxx.t-------------------------</p>
	'''

# -------------------resource data read--------------------------------

def filesize_units(level='m', ksize=1024):

	unit = 'bytes'
	divisor = 0

	if level.lower() == 'k':
		unit = 'K'
		divisor = ksize ** 1
	if level.lower() == 'm':
		unit = 'M'
		divisor = ksize ** 2
	if level.lower() == 'g':
		unit = 'G'
		divisor = ksize ** 3

	if level.lower() == 't':
		unit = 'T'
		divisor = ksize ** 4

	return divisor, unit

def get_cpu_usage():

	return psutil.cpu_percent(interval=1)

def get_memory_usage():

	return psutil.virtual_memory().used, psutil.virtual_memory().total

def get_disk_usage(path='/'):

	info = psutil.disk_usage(path)

	return info.used, info.total, info.free, info.percent

def get_cpu_usage_desc():

	return get_cpu_usage()

def get_memory_usage_desc(level='M'):

	used, total = get_memory_usage()
	divisor, unit = filesize_units(level)

	return '%.2f%s/%.2f%s' % (used / divisor, unit, total / divisor, unit)

def get_disk_usage_string(path='/', level='G'):

	used, total, free, percent = get_disk_usage(path)
	divisor, unit = filesize_units(level)
	
	return '%.2f%s' % (used / divisor, unit), '%.2f%s' % (total / divisor, unit), '%.2f%s' % (free / divisor, unit), '%.2f%%' % (percent), path

def get_disk_usage_desc(path='/', level='G'):

	used, total, free, percent = get_disk_usage(path)
	divisor, unit = filesize_units(level)

	return '%.2f%s/%.2f%s' % (used / divisor, unit, total / divisor, unit)

def get_windows_drives():

	from string import ascii_uppercase

	drives = []

	for s in ascii_uppercase:

		_name = s + ':'

		if os.path.isdir(_name):
			drives.append(_name)

	return drives

def get_linux_paths():



	return [ f'/{d}' for d in os.listdir('/')]

def get_disk_partitions():

	return [(part.mountpoint, part.device, part.fstype) for part in psutil.disk_partitions()]



def platform_type():

	return 'win' if platform.platform().lower().startswith('windows') else ''

def get_platform_info():

	info = {}

	info['platform'] = platform.platform(), '操作系统'
	info['version'] = platform.version(), '系统版本'
	info['processor'] = platform.processor(), '处理器名称'
	info['architecture'] = platform.architecture()[0], '处理器架构'
	info['machine'] = platform.machine(), '计算机类型'
	info['node'] = platform.node(), '计算机名称'
	info['python_version'] = platform.python_version(), 'Python版本'
	info['python_implementation'] = platform.python_implementation(), 'Python解释器'

	return info

def get_resource_usage_info():

	info = {}
	info['cpu_usage'] = get_cpu_usage_desc(), 'CPU占用'
	info['memory_usage'] = get_memory_usage_desc(), '内存占用'

	return info

def get_disk_usage_info(platform='win'):

	if platform == 'win':
		return [get_disk_usage_string(drv) for drv in get_windows_drives()]
	else:
		return [get_disk_usage_string(drv) for drv in get_linux_paths()]

def get_disk_usage_info2():

	return [(*infos, *get_disk_usage_string(infos[0])) for infos in get_disk_partitions()]

def get_network_info():

	info = {}
	net_if_addrs = psutil.net_if_addrs()
	net_if_stats = psutil.net_if_stats()
	info['interfaces'] = []

	for interface, addrs in net_if_addrs.items():
		_addr = {'name': interface, 'isup': net_if_stats[interface].isup}

		for addr in addrs:
			if addr.family == psutil.AF_LINK:
				_addr['mac'] = addr.address
			elif addr.family == socket.AddressFamily.AF_INET:
				_addr['ipv4'] = addr.address
				_addr['netmask'] = addr.netmask

                # if addr.broadcast:
                #     print(f"  广播地址: {addr.broadcast}")
			elif addr.family == socket.AddressFamily.AF_INET6:
				_addr['ipv6'] = addr.address

		info['interfaces'].append(_addr)

	return info



def get_full_info():

	info = {}
	info['platform'] = get_platform_info()
	info['usage'] = get_resource_usage_info()
	info['disk'] = get_disk_usage_info2()
	info['network'] = get_network_info()

	return info

# -------------------process manage--------------------------------

def find_process():

	current_pid = os.getpid()

	print(f'当前pid: {os.getpid()}')

	for proc in psutil.process_iter():

		if proc.pid != current_pid and 'python' in proc.name() and appname in ' '.join(proc.cmdline()):
			print(f"找到进程: PID={proc.pid}, 名称={proc.name()}")
			return proc.pid

	print(f"没有找到其他正在运行的进程")

def find_process_by_port(port):

	current_pid = os.getpid()

	print(f'当前pid: {os.getpid()}')

	for proc in psutil.process_iter():
		connections = proc.net_connections()

		for conn in connections:
			if conn.laddr.port == port:
				print(f"找到进程: PID={proc.pid}, 名称={proc.name()}, cmdline={proc.cmdline()}")
				return proc.pid
		# if proc.pid != current_pid and 'python' in proc.name() and appname in ' '.join(proc.cmdline()):
		# 	print(f"找到进程: PID={proc.pid}, 名称={proc.name()}")
		# 	return proc.pid

	print(f"没有找到其他正在运行的进程")

def kill_process(pid):

	try:
		proc = psutil.Process(pid)
		print(f"关闭正在运行进程: PID={pid}, 名称={proc.name()}, cmdline={proc.cmdline()}")
		proc.kill()
	except Exception as e:
		print(e.args)

	

if __name__ == '__main__':

	import sys

	print(sys.argv)
	hostname = '0.0.0.0'
	port = '8787'


	if len(sys.argv) > 1:
		if sys.argv[1] == 'serv':
			
			backend = 'backend' in sys.argv

			pid = find_process_by_port(int(port))

			if pid :
				if '-f' in sys.argv:
					kill_process(pid)
				else:
					print(f'端口{port}已被占用, 请先关闭进程，或者使用-f')
					os.sys.exit()


			browse(port, hostname=hostname, backend=backend)
		elif sys.argv[1] == 'pid':
			
			pid = find_process_by_port(int(port))

			# print(f'{appname} is running at pid {pid}' if pid else 'process not found')
		else:

			print('invalid args, can try pid, serv')
	else:
		print(get_full_info())

