import click
import win32gui
import win32ui
import win32api
import win32con
import time
import cv2
from PIL import ImageGrab


window_title = 'ClassIn'
window_class = 'Qt5151QWindowIcon'
window_exe = 'ClassIn.exe'

# TODO: 以后写 win32api 自动检测
dpi_scale = 1
bmpfilenamename = "screenshot.bmp"
green = (81, 255, 146)


def capture_screen(hwnd):
	if (hwnd == None):
		hwnd = win32gui.FindWindow(window_class, window_title)
		# TODO: 以后写筛选
	# get window position
	rect = win32gui.GetWindowRect(hwnd)
	x = rect[0]
	y = rect[1]
	w = int((rect[2] - x) * dpi_scale)
	h = int((rect[3] - y) * dpi_scale)
	# take screenshot
	wDC = win32gui.GetWindowDC(hwnd)
	dcObj=win32ui.CreateDCFromHandle(wDC)
	cDC=dcObj.CreateCompatibleDC()
	dataBitMap = win32ui.CreateBitmap()
	dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
	cDC.SelectObject(dataBitMap)
	cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)
	dataBitMap.SaveBitmapFile(cDC, bmpfilenamename)
	# Free Resources
	dcObj.DeleteDC()
	cDC.DeleteDC()
	win32gui.ReleaseDC(hwnd, wDC)
	win32gui.DeleteObject(dataBitMap.GetHandle())
	return x, y, w, h


def find_connected(file_path):
	# read screenshot
	img = cv2.imread(file_path)
	# convert to hsv
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	# find green
	mask = cv2.inRange(hsv, green, green)

	# 搜索图像中的连通区域
	return cv2.connectedComponentsWithStats(mask)


@click.group()
def cli():
	pass


@cli.command()
@click.option('--hwnd', default=None, type=int, help='Window handle')
@click.option('--delay', default=10, type=int, help='Delay (second) between screenshots')
def start_daemon(delay: int, hwnd: int):
	'''
	start daemon
	'''
	while True:
		x, y, w, h = capture_screen(hwnd)

		ret, labels, stats, centroid = find_connected(bmpfilenamename)

		click_cent = None
		for stat, cent in zip(stats, centroid):
			area_width = stat[2] / dpi_scale
			area_height = stat[3] / dpi_scale
			
			if (area_width > w * 0.3 or area_height > h * 0.3):
				continue
			if (area_width < 40 or area_height < 40):
				continue

			# 绘制连通区域
			# cv2.rectangle(img, (stat[0], stat[1]), (stat[0] + stat[2], stat[1] + stat[3]), (25, 25, 255), 3)
			
			click_cent = [int(pos / dpi_scale) for pos in cent]
			break

		if (click_cent != None):
			print(click_cent)
			# 窗口设置为 Foreground
			win32gui.SetForegroundWindow(hwnd)
			time.sleep(1)
			# 发送点击事件
			win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(click_cent[0], click_cent[1]))
			win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(click_cent[0], click_cent[1]))
			# 继续处理

			time.sleep(2)

			screenshot = ImageGrab.grab()  # Take the screenshot
			screenshot.save(bmpfilenamename, 'BMP')

			# read screenshot
			img = cv2.imread(bmpfilenamename)
			# convert to hsv
			hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
			# find green
			mask = cv2.inRange(hsv, green, green)

			ret, labels, stats, centroid = find_connected(bmpfilenamename)

			for stat, cent in zip(stats, centroid):
				area_width = stat[2] / dpi_scale
				area_height = stat[3] / dpi_scale
				
				if (area_width > w * 0.4 or area_height > h * 0.4):
					continue
				if (area_width < 25 and area_height < 25):
					continue

				click_cent = [int(pos / dpi_scale) for pos in cent]
				break
				# img = cv2.imread(bmpfilenamename)
				# 绘制连通区域
				# cv2.rectangle(img, (stat[0], stat[1]), (stat[0] + stat[2], stat[1] + stat[3]), (25, 25, 255), 3)
			
			# click on screen
			if (click_cent != None):
				win32api.SetCursorPos((click_cent[0], click_cent[1]))
				time.sleep(2)
				win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
				time.sleep(.1)
				win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
				time.sleep(.1)
				win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
				return

			print("未找到开始按键")

		print("没有课程可开始")

		time.sleep(delay)


if __name__ == '__main__':
	cli()
