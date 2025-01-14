import os
from sys import executable, exit
from shutil import move
try:
	from msvcrt import getch, kbhit
except:
	def getch() -> str:
		s = input()
		return bytes(s[0]) if s else b"\n"
	def kbhit() -> bool:
		return False
from chardet import detect
from copy import deepcopy
from time import time, sleep
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)
PLATFORM = __import__("platform").system().upper()
CLEAR_SCREEN_COMMAND = ("CLS" if PLATFORM == "WINDOWS" else "clear") if __import__("sys").stdin.isatty() else None



class Music:
	def __init__(self, filePath, version = "v1"):
		self.filePath = filePath
		self.version = version
		try:
			fp = open(filePath, "rb") # must be "rb" here
			self.tags = Music.parse(fp, version)
			fp.close()
		except:
			self.tags = {}
	def getDict(self):
		return {"filePath": self.filePath, "version": self.version, "tags": self.tags}
	def __str__(self):
		return str(self.getDict())
	@staticmethod
	def decodeData(bin_seq): # detect the encoding and make decodings
		result = detect(bin_seq)
		if result["confidence"] > 0:
			try:
				return bin_seq.decode("gbk").rstrip() # remove the spaces at the end
			except:
				return ""
		else:
			return ""
	@staticmethod
	def getTags(tag_data): # obtain the ID3v1 tag data
		STRIP_CHARS = b"\x00"
		tags = {}
		tags["title"] = tag_data[3:33].strip(STRIP_CHARS)
		if (tags["title"]):
			tags["title"] = Music.decodeData(tags["title"])
		tags["artist"] = tag_data[33:63].strip(STRIP_CHARS)
		if (tags["artist"]):
			tags["artist"] = Music.decodeData(tags["artist"])
		tags["album"] = tag_data[63:93].strip(STRIP_CHARS)
		if (tags["album"]):
			tags["album"] = Music.decodeData(tags["album"])
		tags["year"] = tag_data[93:97].strip(STRIP_CHARS)
		if (tags["year"]):
			tags["year"] = Music.decodeData(tags["year"])
		tags["comment"] = tag_data[97:127].strip(STRIP_CHARS)
		if (tags["comment"]):
			tags["comment"] = Music.decodeData(tags["comment"])
		tags["genre"] = ord(tag_data[127:128]) # use [127:128] instead of [127] to fetch [127] to avoid the out-of-bound exception
		return tags
	@staticmethod
	def parse(fileObj, version = "v1"):
		fileObj.seek(0, 2)
		if (fileObj.tell() < 128): # the maximum length of ID3v1 is 128 bit
			return False
		fileObj.seek(-128, 2)
		tag_data = fileObj.read()
		if tag_data[0:3] != b"TAG":
			return False
		return Music.getTags(tag_data)


class WinOS:
	@staticmethod
	def clearScreen(fakeClear:int = 120):
		if CLEAR_SCREEN_COMMAND is not None and not os.system(CLEAR_SCREEN_COMMAND):
			return True
		else:
			try:
				print("\n" * int(fakeClear))
			except:
				print("\n" * 120)
			return False
	@staticmethod
	def clearSpecialChar(fp, special_lists = list("\\/:*?\"<>|"), reserve_names = ["", "nul", "prn", "con", "aux"] + ["com{0}".format(i) for i in range(10)] + ["lpt{0}".format(i) for i in range(10)], target = ""):
		n_fp = os.path.splitext(os.path.split(fp)[1])[0]
		for sChar in special_lists:
			n_fp = n_fp.replace(sChar, target)
		if n_fp.lower() in reserve_names:
			n_fp = str(time()) + "_" + n_fp
		return os.path.join(os.path.split(fp)[0], n_fp + os.path.splitext(fp)[1])
	@staticmethod
	def fixlib(cb, command, inst_1 = None, inst_2 = None, version = None):
		print("未（正确）安装 " + cb + " 库，正在尝试执行安装，请确保您的网络连接正常。")
		if inst_1 == None:
			if version == None:
				os.system("\"" + executable + "\" -m pip install " + cb)
			else:
				os.system("\"" + executable + "\" -m pip install " + cb + "==" + version)
		else:
			os.system(inst_1)
		try:
			exec(command)
		except:
			WinOS.clearScreen()
			if PLATFORM == "WINDOWS" and os.popen("ver").read().upper().find("XP") == -1: # 找不到相关字样
				print("安装 " + cb + " 库失败，正在尝试以管理员权限执行安装，请确保您的网络连接正常。")
				if inst_2 == None: # 提权以管理员身份运行
					if version == None:
						os.system("mshta vbscript:createobject(\"shell.application\").shellexecute(\"" + executable + "\",\"-m pip install " + cb + "\",\"\",\"runas\",\"1\")(window.close)")
					else:
						os.system("mshta vbscript:createobject(\"shell.application\").shellexecute(\"" + executable + "\",\"-m pip install " + cb + "==" + version + "\",\"\",\"runas\",\"1\")(window.close)")
				else:
					os.system(inst_2)
				print("已弹出新窗口，确认授权并安装完成后，请按任意键继续。")
				os.system("pause>nul&cls")
				try:
					exec(command)
				except:
					print("无法正确安装 " + cb + " 库，请按任意键退出，建议稍后重新启动本程序。")
					os.system("pause>nul&cls")
					exit(EOF)
			else:
				print("无法正确安装 " + cb + " 库，请按任意键退出，建议稍后重新启动本程序。")
				os.system("pause>nul&cls")
				exit(EOF)
	@staticmethod
	def cdCurrentPath() -> bool:
		try:
			os.chdir(os.path.abspath(os.path.dirname(__file__))) # 解析进入程序所在目录
			return True
		except:
			return False
	@staticmethod
	def osWalk(target_path, extent = None, caseSen = (PLATFORM != "WINDOWS")): # 遍历文件夹
		allPath = []
		for base_path, folder_list, file_list in os.walk(target_path):
			for file_name in file_list:
				file_path = os.path.join(base_path, file_name)
				if extent == None: # 无筛选
					allPath.append(file_path)
					continue
				file_ext = file_path.rsplit(".", maxsplit = 1)
				if len(file_ext) != 2: # 没有后缀名
					if extent == "": # 如果仅筛选无后缀名文件
						allPath.append(file_path)
					continue # 无论是否有后缀名都进行 continue
				if type(extent) == str: # 字符串
					if caseSen: # 大小写敏感
						if file_ext[1] == extent:
							allPath.append(file_path)
					else: # 大小写不敏感
						if file_ext[1].lower() == extent.lower():
							allPath.append(file_path)
				elif type(extent) in (tuple, list, set): # 常见系列数据
					if caseSen: # 大小写敏感
						if file_ext[1] in extent:
							allPath.append(file_path)
					else: # 大小写不敏感
						for _ext in extent:
							if file_ext[1].lower() == _ext.lower():
								allPath.append(file_path)
								break
		return allPath
	@staticmethod
	def sepClass(root_path, dic): # 分类器
		rp = str(root_path).replace("\"", "").replace("\'", "").replace("\\", "/") # 去掉引号并将目录分层符泛化
		if rp[-1] == "/" or rp[-1] == "\\":
			rp = rp[:-1]
		if not os.path.exists(rp): # 根目录不存在
			return (False, "No such file or directory")
		rp += "/"
		errorDict = {}
		try:
			for folder in list(dic.keys()):
				if not os.path.exists(rp + folder):
					os.mkdir(rp + folder)
				for file in dic[folder]:
					try:
						move(rp + file, rp + folder)
					except Exception as ee:
						errorDict.setdefault(rp + file, ee)
			if len(errorDict) == 0:
				return True
			else:
				return (True, errorDict)
		except Exception as e:
			return (False, e)
	@staticmethod
	def changeGlobal(): # 切换清华源
		os.system("pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple")
		os.system("pip config set global.timeout 120")


class Path:
	def __init__(self:object, path:str|object = ".", isWindows:bool = True, workingDirectories:dict = {}) -> object:
		self.__originalPath = str(path) if isinstance(path, (str, Path)) else "."
		self.__isWindows = not (hasattr(isWindows, "__bool__") and not bool(isWindows)) # must be not (A or not B)
		if self.__isWindows and isinstance(workingDirectories, dict): # Windows && parameters passed are valid
			self.__workingDirectories = {}
			for key in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
				# Record #
				if key + ":" in workingDirectories:
					self.__workingDirectories[key + ":"] = str(workingDirectories[key + ":"]).replace("/", "\\") if isinstance(workingDirectories[key + ":"], (str, Path)) else "\\"
				elif key.lower() + ":" in workingDirectories:
					self.__workingDirectories[key + ":"] = str(workingDirectories[key.lower() + ":"]).replace("/", "\\") if isinstance(workingDirectories[key.lower() + ":"], (str, Path)) else "\\"
				elif key in workingDirectories:
					self.__workingDirectories[key + ":"] = str(workingDirectories[key]).replace("/", "\\") if isinstance(workingDirectories[key], (str, Path)) else "\\"
				elif key.lower() in workingDirectories:
					self.__workingDirectories[key + ":"] = str(workingDirectories[key.lower()]).replace("/", "\\") if isinstance(workingDirectories[key.lower()], (str, Path)) else "\\"
				else:
					self.__workingDirectories[key + ":"] = "\\"
					continue # this continue stops the recursion
				
				# Uniform #
				if self.__workingDirectories[key + ":"].startswith(key + ":") or self.__workingDirectories[key + ":"].startswith(key.lower() + ":"):
					self.__workingDirectories[key + ":"] = str(Path(self.__workingDirectories[key + ":"][2:], isWindows = self.__isWindows))
				elif self.__workingDirectories[key + ":"].startswith("\\"):
					self.__workingDirectories[key + ":"] = str(Path(self.__workingDirectories[key + ":"], isWindows = self.__isWindows))
				else: # invalid
					self.__workingDirectories[key + ":"] = "\\"
		else:
			self.__workingDirectories = {}
		self.__resolve()
	def __resolve(self:object) -> None:
		# Initialize #
		if self.__isWindows: # Windows
			if (																																							\
				2 == len(self.__originalPath) and ("A" <= self.__originalPath[0] <= "Z" or "a" <= self.__originalPath[0] <= "z") and ":" == self.__originalPath[1]										\
				 or len(self.__originalPath) >= 3and ("A" <= self.__originalPath[0] <= "Z" or "a" <= self.__originalPath[0] <= "z") and ":" == self.__originalPath[1] and "\\" == self.__originalPath[2]		\
			): # starts with a drive letter
				self.__driveLetter = self.__originalPath[0].upper() + ":"
				self.__convertedPath = self.__originalPath[2:].replace("/", "\\")
			else:
				self.__driveLetter = ""
				self.__convertedPath = self.__originalPath.replace("/", "\\")
			self.__sep = "\\"
			self.__reserves = ["CON", "PRN", "AUX", "NUL"] + ["COM{0}".format(i) for i in range(10)] + ["LPT{0}".format(i) for i in range(10)]
		else:
			self.__driveLetter = ""
			self.__convertedPath = self.__originalPath
			self.__sep = "/"
			self.__reserves = []
		
		# Convert #
		if self.__convertedPath:
			# Remove all the repeated path separators #
			vec = list(self.__convertedPath)
			i = 0
			while i < len(vec) - 1: # the length cannot be fixed to speed up here
				if self.__sep == vec[i] and self.__sep == vec[i + 1]:
					del vec[i + 1]
				else:
					i += 1
			self.__convertedPath = "".join(vec)
			
			# merge "." and ".." #
			vec = self.__convertedPath.split(self.__sep)
			i = 1
			while i < len(vec):
				if "." == vec[i]: # we do not remove the first "." here
					del vec[i]
				elif ".." == vec[i]:
					if vec[i - 1] in (".", ".."): # can do nothing if it is "." or ".."
						i += 1
					elif 1 == i and (not vec[0] or 2 == len(vec[0]) and "A" <= vec[0][0] <= "Z" and ":" == vec[0][1]): # ".." of the root is still the root
						del vec[i] # only remove the current ..
					else:
						del vec[i]
						del vec[i - 1]
						i = max(i - 1, 1) # avoid 0
				else:
					i += 1
			if len(vec) >= 2:
				if "." == vec[0] and vec[1]:
					del vec[0]
				self.__convertedPath = self.__sep.join(vec)
			elif 1 == len(vec):
				if vec[0]:
					self.__convertedPath = vec[0]
				else:
					self.__convertedPath = self.__sep
			else:
				self.__convertedPath = "."
			
			# Call strip() for Windows objects #
			#if self.__isWindows:
			#	vec = self.__convertedPath.split(self.__sep)
			#	for i in range(len(vec)):
			#		vec[i] = vec[i].strip()
			#	self.__convertedPath = self.__sep.join(vec)
		else:
			self.__convertedPath = self.__workingDirectories[self.__driveLetter] if self.__isWindows and self.__driveLetter else "."
	def isValid(self:object) -> bool:
		vec = self.__convertedPath.split(self.__sep)
		if self.__isWindows:
			for v in vec:
				if len(v) > 255 or ":" in v or "*" in v or "?" in v or "\"" in v or "<" in v or ">" in v or "|" in v or v.upper() in self.__reserves or not v.isprintable():
					return False
			return len(str(self)) <= 32762 # length
		else:
			for v in vec:
				if "\0" in v or len(bytes(v, encoding = "utf-8")) > 255:
					return False
			return True
	def isAbsolute(self:object) -> bool:
		return self.__convertedPath.startswith(self.__sep)
	def isRelative(self:object) -> bool:
		return not self.__convertedPath.startswith(self.__sep)
	def exists(self:object) -> bool:
		return os.path.exists(str(self))
	def isdir(self:object) -> bool:
		return os.path.isdir(str(self))
	def isfile(self:object) -> bool:
		return os.path.isfile(str(self))
	def islink(self:object) -> bool:
		return os.path.islink(str(self))
	def readlink(self:object) -> str|BaseException:
		try:
			return os.readlink(str(self))
		except BaseException as e:
			return e
	def create(self:object, parameter:None|bool = None) -> None|BaseException:
		path = str(self)
		try:
			if path.endswith(self.__sep) or True == parameter: # create a folder
				os.makedirs(path)
				return None
			else: # create a file
				bRet = Path(self.__sep.join(path.split(self.__sep)[:-1]), isWindows = self.__isWindows).create(True)
				if bRet is None:
					with open(path, "wb") as f:
						return None
				else:
					return  bRet
		except BaseException as e:
			return e
	def setPath(self:object, path:str|object) -> bool:
		if isinstance(path, (str, Path)):
			self.__originalPath = str(path)
			self.__resolve()
			return True
		else:
			return False
	def getPath(self:object) -> str:
		return str(self)
	def setIsWindows(self:object, isWindows:bool) -> bool:
		if hasattr(isWindows, "__bool__"):
			self.__isWindows = bool(isWindows)
			return True
		else:
			return False
	def getIsWindows(self:object) -> bool:
		return self.__isWindows
	def setWorkingDirectory(self:object, key:str, value:str|object) -> bool:
		if self.__isWindows and isinstance(key, str) and isinstance(value, (str, Path)):
			# Set #
			if 1 == len(key) and ("A" <= key <= "Z" or "a" <= key <= "z"):
				realKey = key.upper() + ":"
			elif 2 == len(key) and ("A" <= key[0] <= "Z" or "a" <= key[0] <= "z") and ":" == key[1]:
				realKey = key.upper()
			else:
				return False
			
			# Check #
			self.__workingDirectories[realKey] = str(value)
			if self.__workingDirectories[realKey].startswith(realKey) or self.__workingDirectories[realKey].startswith(realKey.lower()):
				self.__workingDirectories[realKey] = str(Path(self.__workingDirectories[realKey][2:]))
				return True
			elif self.__workingDirectories[realKey].startswith("\\"): # valid
				self.__workingDirectories[realKey] = str(Path(self.__workingDirectories[realKey]))
				return True
			else:
				return False
		else:
			return False
	def setWorkingDirectories(self:object, workingDirectories:dict) -> int:
		if self.__isWindows and isinstance(workingDirectories, dict):
			cnt = 0
			for key, value in workingDirectories.items():
				if self.setWorkingDirectory(key, value):
					cnt += 1
			return cnt
		else:
			return -1
	def getWorkingDirectory(self:object, driveLetter:str) -> str:
		return self.__workingDirectories[driveLetter[0].upper() + ":"] if isinstance(driveLetter, str) and (1 == len(driveLetter) or 2 == len(driveLetter) and ":" == driveLetter[1]) and ("A" <= driveLetter[0] <= "Z" or "a" <= driveLetter[0] <= "z") else None
	def getWorkingDirectories(self:object) -> dict:
		return deepcopy(self.__workingDirectories)
	@staticmethod
	def join(paths:tuple|list, isWindows:bool = True, workingDirectories:dict = {}) -> object:
		vec = []
		for p in paths:
			if hasattr(p, "__str__"):
				vec.append(str(p))
		return Path(("/" if hasattr(isWindows, "__bool__") and not bool(isWindows) else "\\").join(vec), isWindows = isWindows, workingDirectories = workingDirectories)
	@staticmethod
	def abspath(relPath:str|object, currentPath:None|str|object = None, isWindows:bool = True, workingDirectories:dict = {}) -> object:
		if hasattr(relPath, "__str__"):
			p = Path(relPath, isWindows = isWindows, workingDirectories = workingDirectories)
			if p.isAbsolute(): # (ABS, --)
				return p
			elif hasattr(currentPath, "__str__") and Path(currentPath, isWindows = isWindows, workingDirectories = workingDirectories).isAbsolute(): # (REL, ABS)
				Path(currentPath, isWindows = isWindows, workingDirectories = workingDirectories) + relPath
			else: # (REL, REL) or (REL, )
				return Path(os.path.abspath(str(Path(currentPath, isWindows = isWindows, workingDirectories = workingDirectories) + relPath)))
		else:
			return Path(".", isWindows = isWindows, workingDirectories = workingDirectories)
	@staticmethod
	def relpath(absPath:str|object, basePath:str|object, currentPath:None|str|object = None, isWindows:bool = True, workingDirectories:dict = {}) -> object:
		if hasattr(absPath, "__str__") and hasattr(basePath, "__str__"):
			p1, p2 = Path.abspath(absPath, currentPath, isWindows = isWindows, workingDirectories = workingDirectories), Path.abspath(basePath, currentPath, isWindows = isWindows, workingDirectories = workingDirectories)
			try:
				return Path(os.path.relpath(str(p1), str(p2)), isWindows = isWindows, workingDirectories = workingDirectories)
			except BaseException as e:
				return e
		else:
			return Path(".", isWindows = isWindows, workingDirectories = workingDirectories)
	def __add__(self:object, other:str|object) -> object:
		return Path(str(self) + str(other), isWindows = self.__isWindows, workingDirectories = deepcopy(self.__workingDirectories)) if hasattr(other, "__str__") else Path(str(self))
	def __iadd__(self:object, other:str|object) -> None:
		if hasattr(other, "__str__"):
			self.__originalPath += str(other)
			self.__resolve()
	def __str__(self:object) -> str:
		return self.__driveLetter + self.__convertedPath if self.__isWindows and self.__driveLetter else self.__convertedPath


class PyTools:
	@staticmethod
	def showAll(): # display all the third-party Python libraries
		with os.popen("\"{0}\" -m pip list".format(executable)) as hdle:
			dists = hdle.read()
		print(dists)
	@staticmethod
	def showOutdated(): # display all the third-party Python libraries that can be updated
		os.system("\"{0}\" -m pip list --outdate".format(executable))
	@staticmethod
	def updateAll(): # update all the third-party Python libraries
		os.system("\"{0}\" -m pip install --upgrade pip".format(executable))
		with os.popen("\"{0}\" -m pip list".format(executable)) as hdle:
			dists = hdle.read()
		package_name = [dist.split(" ")[0] for dist in dists.split("\n")][2:-1]
		print(package_name)
		for dist in package_name:
			os.system("\"{0}\" -m pip install --upgrade {1}".format(executable, " ".join(package_mame)))
	@staticmethod
	def debug():
		def __debug() -> int|None:
			__statement, __flag = input(">>> "), False # the flag is used to indicate the ":"
			if __statement.lstrip().startswith("!!"):
				os.system("START /REALTIME \"\" " + __statement[2:] if "WINDOWS" == PLATFORM else __statement[2:]  + " &")
				return None
			elif __statement.lstrip().startswith("!"):
				print(os.system(__statement[1:]))
				return None
			elif __statement.lstrip().startswith("#"):
				return None
			while True:
				__stack = []
				__i = 0
				while __i < len(__statement):
					__ch = __statement[__i]
					if __ch in ("(", "[", "{"):
						if not (__stack and __stack[-1] in ("\"", "\'", "\"" * 3, "\'" * 3)):
							__stack.append(__ch)
					elif __ch in (")", "]", "}"):
						if __stack and __stack[-1] == {")":"(", "]":"[", "}":"{"}[__ch]:
							__stack.pop()
						elif not (__stack and __stack[-1] in ("\"", "\'", "\"" * 3, "\'" * 3)):
							__stack.clear() # ask the Python to throw exceptions directly
							break
					elif "\"" == __ch:
						if not (__stack and __stack[-1] in ("\'", "\'" * 3)):
							if __stack and __stack[-1] == "\"":
								__stack.pop()
							elif __stack and __stack[-1] == "\"" * 3:
								if __statement[__i:__i + 3] == "\"" * 3:
									__stack.pop()
									__i += 2 # skip two chars
							elif __statement[__i:__i + 3] == "\"" * 3:
								__stack.append("\"" * 3)
								__i += 2
							else:
								__stack.append("\"")
					elif "\'" == __ch:
						if not (__stack and __stack[-1] in ("\"", "\"" * 3)):
							if __stack and __stack[-1] == "\'":
								__stack.pop()
							elif __stack and __stack[-1] == "\'" * 3:
								if __statement[__i:__i + 3] == "\'" * 3:
									__stack.pop()
									__i += 2 # skip two chars
							elif __statement[__i:__i + 3] == "\'" * 3:
								__stack.append("\'" * 3)
								__i += 2
							else:
								__stack.append("\'")
					elif "\\" == __ch:
						if __stack and __stack[-1] in ("\"", "\'", "\"" * 3, "\'" * 3):
							__i += 1 # skip a char
						else:
							__stack.clear() # ask the Python to throw exceptions directly
							break
					elif "#" == __ch:
						if not (__stack and __stack[-1] in ("\"", "\'", "\"" * 3, "\'" * 3)): # the remaining strings are commented
							__statement = __statement[:__i]
							__stack.clear()
							break
					__i += 1
					del __ch
				if  __stack and __stack[-1] not in ("\"", "\'"):
					__statement = __statement + "\n" + input("... ")
				elif  __statement and __statement.split("\n")[-1].rstrip().endswith(":"):
					__statement = __statement + "\n" + input("... ")
					__flag = True
				elif __flag and __statement and __statement.split("\n")[-1]:
					__statement = __statement + "\n" + input("... ")
				else:
					del __stack, __i, __flag
					break
			if __statement.replace(" ", "").replace("\t", "") in ("exit()", "quit()"):
				return 0
			elif (__statement.replace(" ", "").replace("\t", "").startswith("exit(") or __statement.replace(" ", "").replace("\t", "").startswith("quit(")) and __statement.replace(" ", "").replace("\t", "").endswith(")"): # there are only one statement per line
				try:
					__res = eval(__statement[__statement.index("(") + 1:-__statement[::-1].index(")") - 1])
					return __res if isinstance(__res, int) else 1
				except BaseException as __e:
					print(__e)
			try:
				__res = eval(__statement)
				if __res is not None:
					print(__res)
				del __res
			except:
				try:
					exec(__statement)
				except KeyboardInterrupt:
					print("\nKeyboardInterrupt")
				except BaseException as __e:
					print(__e)
			return None
		while True:
			try:
				__exitCode = __debug()
				if __exitCode is not None:
					break
			except KeyboardInterrupt:
				print("\nKeyboardInterrupt")
			except BaseException as e:
				print(e)
		exit(__exitCode)
	@staticmethod
	def convertEscaped(string:str) -> str:
		if isinstance(string, str):
			vec = list(string)
			d = {"\\":"\\\\", "\"":"\\\"", "\'":"\\\'", "\a":"\\a", "\b":"\\b", "\f":"\\f", "\n":"\\n", "\r":"\\r", "\t":"\\t", "\v":"\\v"}
			for i, ch in enumerate(vec):
				if ch in d:
					vec[i] = d[ch]
				elif not ch.isprintable():
					vec[i] = "\\x" + hex(ord(ch))[2:]
			return "\'" + "".join(vec) + "\'"
		else:
			return str(string)
	@staticmethod
	def getTxt(filePath:str) -> str|None: # get ``*.txt`` content
		for coding in ("utf-8", "ANSI", "utf-16", "gbk"): # codings (add more codings here if necessary)
			try:
				with open(filePath, "r", encoding = coding) as f:
					content = f.read()
				return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
			except (UnicodeError, UnicodeDecodeError):
				continue
			except:
				return None
		return None
	@staticmethod
	def handleFolder(fd:str) -> bool:
		folder = str(fd)
		if not folder:
			return True
		elif os.path.exists(folder):
			return os.path.isdir(folder)
		else:
			try:
				os.makedirs(folder)
				return True
			except:
				return False
	@staticmethod
	def press_any_key_to_continue() -> bytes:
		while kbhit():
			getch()
		return getch()
	@staticmethod
	def preExit(countdownTime:int = 5) -> None:
		try:
			cntTime = int(countdownTime)
			length = len(str(cntTime))
		except:
			print("Program ended. ")
			return
		print()
		while cntTime > 0:
			print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime), end = "")
			try:
				sleep(1)
			except:
				print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(0))
				return
			cntTime -= 1
		print("\rProgram ended, exiting in {{0:>{0}}} second(s). ".format(length).format(cntTime))





if __name__ == "__main__":
	PyTools.debug()