import requests, re, os, platform, datetime

def init():
    """
    Initialize global variable and const
    """
    global r, CAPTCHA_ELEMENT_ID, BROWSER_HEADERS, SUCCESS, FAILURE, home_url, tkb_url, subject_tooltip_pattern, student_id, student_name, student_id_pattern, teacher_id_pattern, date_of_year, EXIT, VIEW_BY_ID, cmd_clear
    EXIT = 0
    VIEW_BY_ID = 1
    student_id_pattern = r"[a-zA-Z]{1}[0-9]{2}[a-zA-Z]{4}[0-9]{3}"
    teacher_id_pattern = r"[a-zA-Z]{2}[0-9]{4}"
    subject_tooltip_pattern = r"<td onmouseover=\"ddrivetip\((.*),''.*>"
    SUCCESS = True
    FAILURE = False
    BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8,ko;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    r = requests.Session()
    CAPTCHA_ELEMENT_ID = "ctl00_ContentPlaceHolder1_ctl00_lblCapcha"
    home_url = 'http://qldt.ptit.edu.vn/Default.aspx?page=gioithieu'
    tkb_url = 'http://qldt.ptit.edu.vn/Default.aspx?sta=0&page=thoikhoabieu&id='
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        print("[*] System detected -> {}".format(platform.system()))
        hosts_path = '/etc/hosts'
        cmd_clear = 'clear'
    elif platform.system() == 'Windows':
        print("[*] System detected -> {}".format(platform.system()))
        hosts_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
        cmd_clear = 'cls'

def clear():
    global cmd_clear
    os.system(cmd_clear)
    return

class Qldt:
    session = requests.Session()
    def init_home_page(self):
        """
        If this method return SUCCESS, this Object will be access qldt.ptit.edu.vn without Captcha asked!

        Return:
            True: if bypass captcha SUCCESS or no-captcha detected
            False: if bypass captcha FAILURE
        """
        rps = self.session.get(home_url, headers = BROWSER_HEADERS)
        # with open('first_get.html', 'w') as f: f.write(rps.text)
        if CAPTCHA_ELEMENT_ID in rps.text:
            # print("CAPTCHA ELEMENT DETECTED!")
            return self.bypass_captcha(rps.text)
        else:
            print("NO CAPTCHA")
        return True
    def bypass_captcha(self, rps):
        """
        This method send bypass captcha requests to server.
        Before this method: this object will be asked for captcha when access qldt.ptit.edu.vn
        After this method: this object has free-access to qldt.ptit.edu.vn.

        Args:
            rps: String object, HTML source code include captcha inside.
        Return:
            true if success
            false if failure
        """
        viewstate_pattern = r"id=\"__VIEWSTATE\".*\"(.*)\""
        viewstategenerator_pattern = r"id=\"__VIEWSTATEGENERATOR\".*\"(.*)\""
        CAPTCHA_PATTERN = r"id=\"ctl00_ContentPlaceHolder1_ctl00_lblCapcha\".*?>(.*?)<\/span>"
        viewstate = re.search(viewstate_pattern, rps)
        if viewstate:
            viewstate = viewstate.group(1)
        else:
            print("VIEWSTATE value not found!")
        viewstategenerator = re.search(viewstategenerator_pattern, rps)
        if viewstategenerator:
            viewstategenerator = viewstategenerator.group(1)
        captcha = re.search(CAPTCHA_PATTERN, rps)
        if captcha:
            captcha_text = captcha.group(1)
            print("[*] CAPTCHA -> [{}]".format(captcha_text))
            payload = {
                'ctl00$ContentPlaceHolder1$ctl00$txtCaptcha':captcha_text,
                '__VIEWSTATE':viewstate,
                '__VIEWSTATEGENERATOR':viewstategenerator,
                '__EVENTARGUMENT':'',
                '__EVENTTARGET':'',
                'ctl00$ContentPlaceHolder1$ctl00$btnXacNhan': 'Vào website'
            }
            rps = self.session.post(url = home_url, headers = BROWSER_HEADERS, data=payload)
            if CAPTCHA_ELEMENT_ID not in rps.text:
                print("[*] CAPTCHA BYPASSED")
                return True
            else:
                print("CAPTCHA NOT BYPASSED! PLEASE REPORT TO DEVELOPER BACHVKHOA!")
        else:
            print("[*] CAPTCHA NOT FOUND")
        return False
    def view_schedule(self, uid):
        url = tkb_url + uid
        rps = self.session.get(url)
        return self
    def print_schedule_post(self, uid):
        url = 'http://qldt.ptit.edu.vn/ajaxpro/EduSoft.Web.UC.ThoiKhoaBieu,EduSoft.Web.ashx'
        headers = {
            'Content-Type':'text/plain; charset=UTF-8',
            'X-AjaxPro-Method':'LoadDatatablePrint',
            'Referer':'http://qldt.ptit.edu.vn/default.aspx?page=thoikhoabieu&sta=1&id='+uid
        }
        payload = {
            'value':'false'
        }
        rps = self.session.post(url = url, headers = headers)
        # print('PRINTED TO FILE')
        # with open('printtable_afterpost.html', 'w') as f: f.write(rps.text)
        return self
    def get_schedule_raw_html(self, uid):
        url = 'http://qldt.ptit.edu.vn/Report/TKBReportView.aspx'
        headers = {
            'Referer':'http://qldt.ptit.edu.vn/default.aspx?page=thoikhoabieu&sta=0&id='+uid
        }
        rps = self.session.get(url = url, headers = headers)
        # with open('printtable_afterget.html', 'w') as f: f.write(rps.text)
        # print("Printed to get-file")
        viewstate_ptrn = r'id=\"__VIEWSTATE\" value=\"(.*)\"'
        viewstategen_prtn = r'id=\"__VIEWSTATEGENERATOR\" value=\"(.*)\"'
        eventvalidation_ptrn = r'id=\"__EVENTVALIDATION\" value=\"(.*)\"'
        viewstate = re.search(viewstate_ptrn, rps.text).group(1)
        viewstategen = re.search(viewstategen_prtn, rps.text).group(1)
        eventvalidation = re.search(eventvalidation_ptrn, rps.text).group(1)
        payload = {
            'StiWebViewer1$PageNumber': '1',
            '__CALLBACKID':'StiWebViewer1',
            '__CALLBACKPARAM':'ViewModeWholeReport',
            '__EVENTARGUMENT':'',
            '__EVENTTARGET':'',
            '__VIEWSTATE':viewstate,
            '__VIEWSTATEGENERATOR':viewstategen,
            '__EVENTVALIDATION':eventvalidation
        }
        rps = self.session.post(url = url, data = payload)
        # req_headers = {
        #     'Host':' qldt.ptit.edu.vn',
        #     'Connection':' keep-alive',
        #     'Upgrade-Insecure-Requests':' 1',
        #     'User-Agent':' Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        #     'Accept':' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        #     'Referer':' http://qldt.ptit.edu.vn/Report/TKBReportView.aspx',
        #     'Accept-Encoding':' gzip, deflate',
        #     'Accept-Language':' en-US,en;q=0.9,vi;q=0.8,ko;q=0.7'
        # }
        url1255 = 'http://qldt.ptit.edu.vn' + rps.text.split(';')[9]
        rps = self.session.get(url1255)
        with open(uid+'_'+datetime.datetime.now().strftime('%d-%m-%Y')+'.html', 'wb') as f: f.write(rps.content)
        return rps.content
    def export_info_from_raw_html(self, raw):
        raw = raw.decode('utf-8')
        info_pattern = r'class=\"[a-zA-Z0-9]{9}\".+?>(.+?)<'
        raw = raw.replace('&nbsp;', '')
        infors = re.findall(info_pattern, raw)
        print("\n * * * R E S U L T * * *\n ")
        print(' {} -> {}\n{} -> {}\n{} -> {}\n{} -> {}\n'.format(infors[6],infors[7],infors[8],infors[9],infors[10],infors[11],infors[12],infors[13]))
        print("\n * * * * * * * * * * * *\n ")

def menu():
    global EXIT, VIEW_BY_ID
    while True:
        print("    ***   P T I T   S T U D E N T   I N F O   F E T C H E R ***")
        print("[{}] View info by student_id".format(VIEW_BY_ID))
        print("[{}] Exit".format(EXIT))
        cmd = int(input("Enter your choice: "))
        clear()
        if cmd == VIEW_BY_ID:
            student_id = input("student id: ").upper()
            qldt = Qldt()
            qldt.init_home_page()
            raw = qldt.view_schedule(student_id).print_schedule_post(student_id).get_schedule_raw_html(student_id)
            qldt.export_info_from_raw_html(raw)
        elif cmd == EXIT:
            break
    return
def main():
    init()
    menu()
    

if __name__ == '__main__':
    main()