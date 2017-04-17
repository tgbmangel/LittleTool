#coding:cp936
import paramiko
import Tkinter as tk
import tkMessageBox
import time
import sys
import os
import ttk

#打包程序用的是pyinstaller 3.2，命令行直接执行：pyinstaller -Fw buildcloudlittletool.py
#pyinstaller --clean --win-private-assemblies -Fw --icon=wisonic.ico buildcloudlittletool.py
#pyinstaller buildcloudlittletool.spec(最新使用，用来打包pem文件)

def get_info():
    #获取输入框信息，用户名密码为空直接返回，不然就返回所有信息
    doctor_hospital=dhospital.get()
    doctor_department=ddepartment.get()
    doctor_position=dposition.get()
    doctor_name=dname.get()
    doctor_login_name=dusername.get()
    doctor_pwd=dpwd.get()
    create_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    if doctor_login_name.strip()=='':
        tkMessageBox.showinfo(title='done',message=u"请输入有效用户名")
        return
    if doctor_pwd.strip()=='':
        tkMessageBox.showinfo(title='done',message=u"请输入有效密码")
        return
    return doctor_hospital,doctor_department,doctor_position,doctor_name,doctor_login_name,doctor_pwd,create_time

def exe_sql(sql):
    #数据库密码是写死的。- -~不想写太多外部传入的
    if host[1]=="ec2-user":
        cmd_sql="mysql -h host -P 3306 -uuser -pwd -Dxxx -e '%s'" %sql
    else:
        cmd_sql="mysql -uuser -pwd -Dxxx -e '%s'" %sql
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd_sql)
        return stdin, stdout, stderr
    except Exception as e:
        tkMessageBox.showinfo(title=' ',message=e)

def sql_insert():#添加账号
    if not get_info():
        pass
    else:
        doctor_hospital,doctor_department,doctor_position,doctor_name,doctor_login_name,doctor_pwd,cttime=get_info()
        sql='INSERT INTO wc_doctor_user_info(name,userName,password,hospital,department,position,createTime) ' \
            'VALUES ( "%s","%s","%s","%s","%s","%s","%s");'\
            %(doctor_name,doctor_login_name,doctor_pwd,doctor_hospital,doctor_department,doctor_position,cttime)
        sql_register='INSERT INTO wc_doctor_user_register_info(name,userName,password,hospital,department,position,createTime) ' \
            'VALUES ( "%s","%s","%s","%s","%s","%s","%s");' \
            %(doctor_name,doctor_login_name,doctor_pwd,doctor_hospital,doctor_department,doctor_position,cttime)
        try:
            stdin, stdout, stderr=exe_sql(sql)
            stdin, stdout, stderr=exe_sql(sql_register)
            sqlerror=stderr.read()#临时的工具，目前看不出多条执行是哪条出错，先不改
            if sqlerror:
                #返回sql执行的错误信息
                tkMessageBox.showinfo(title=' ',message=sqlerror)
            else:
                tkMessageBox.showinfo(title=' ',message=u"添加成功")
        except Exception as e:
            tkMessageBox.showinfo(title=' ',message=e)
        Insert_button.configure(state="disabled")

def account_check():#账号查询
    doctor_login_name=dusername.get()
    if doctor_login_name.strip()=='':
        tkMessageBox.showinfo(title=' ',message=u"请输入有效用户名")
        return
    else:
        sql_check='select id from wc_doctor_user_info where userName="%s";' %doctor_login_name
        try:
            stdin, stdout, stderr=exe_sql(sql_check)
            search_result=stdout.read()
            if search_result:
                tkMessageBox.showinfo(title=' ',message=u"已存在相同账号")
                Insert_button.configure(state="disabled")
                Insert_button.flash()
            else:
                tkMessageBox.showinfo(title=' ',message=u"账号可用")
                Insert_button.configure(state="active")
                Insert_button.flash()

            sqlerror=stderr.read()
            if sqlerror:
                tkMessageBox.showinfo(title=' ',message=sqlerror)

        except Exception as e:
            tkMessageBox.showinfo(title=' ',message=e)

def create_qun():
    #群创建
    createqun_qun_name=qun_name.get()
    createqun_zuzhi_name=zuzhi_name.get()
    createqun_bumen_name=bumen_name.get()
    createqun_admin_name=admin_name.get()
    createqun_time=time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    if createqun_qun_name.strip()=='':
        tkMessageBox.showinfo(title=' ',message=u"请输入有效的群名称")
        return
    if createqun_admin_name.strip()=='':
        tkMessageBox.showinfo(title=' ',message=u"请输入有效的群主账号")
        return
    createqun_sql='INSERT INTO wc_group_info(groupName,company,department,createTime) ' \
                  'VALUES ("%s","%s","%s","%s");' \
                  %(createqun_qun_name,createqun_zuzhi_name,createqun_bumen_name,createqun_time)
    try:
        stdin, stdout, stderr=exe_sql(createqun_sql)
        sqlerror=stderr.read()
        if sqlerror:
            #返回sql执行的错误信息
            tkMessageBox.showinfo(title=' ',message=sqlerror)
    except Exception as e:
        tkMessageBox.showinfo(title=' ',message=e)
    qunID_sql='select id from wc_group_info where groupName="%s";'%createqun_qun_name
    try:
        stdin, stdout, stderr=exe_sql(qunID_sql)
        qunID=stdout.read()
        qid=qunID.split("id")[-1].strip()
        global qunzhu_sql
        qunzhu_sql='INSERT INTO wc_group_user(userName, permission,groupId,status,createTime) ' \
                   'VALUES ("%s","11","%s","1","%s");'%(createqun_admin_name,qid,createqun_time)
    except Exception as e:
        tkMessageBox.showinfo(title=' ',message=e)
    try:
        stdin, stdout, stderr=exe_sql(qunzhu_sql)
        sqlerror=stderr.read()
        if sqlerror:
            #返回sql执行的错误信息
            tkMessageBox.showinfo(title=' ',message=sqlerror)
        else:
            tkMessageBox.showinfo(title=' ',message=u"群添加成功")
    except Exception as e:
        tkMessageBox.showinfo(title=' ',message=e)

def show_all_qun():
    #显示群以及群主信息，避免多次添加同一个群、或者同一个群主有多个群
    clear_text_area()
    allQunSql='select a.groupName,b.userName,a.createTime from wc_group_info a,wc_group_user b ' \
              'where b.groupId=a.id and b.permission="11" order by createTime desc;'
    try:
        stdin, stdout, stderr=exe_sql(allQunSql)
        ShowQun=stdout.read()
        QunList=ShowQun.split("\n")[1:-1]
        textqun.insert(tk.END,u"群主：           "+"    "+u"创建时间："+"                 "+u"群名称：")
        for x in QunList:
            NameAndAdmin=x.split("\t")
            textqun.insert(tk.END,NameAndAdmin[1]+"    "+NameAndAdmin[2]+"    "+NameAndAdmin[0])
        for i in range(len(QunList)+1):
            textqun.itemconfig(i,bg="#D3D3D3")
            if i%2==0:
                textqun.itemconfig(i,bg="#C0C0C0")
    except Exception as e:
        tkMessageBox.showinfo(title=' ',message=e)

def show_user_info():
    #本来想显示所有用户，想想没必要，每次产品都是找我查单个人的信息
    doctor_login_name=dusername.get()
    if doctor_login_name.strip()=='':
        tkMessageBox.showinfo(title=' ',message=u"请在【*医生账号】处输入有效用户名")
        return
    clear_text_area()
    allQunSql='select userName,password,name,hospital,createTime ' \
              'from wc_doctor_user_info where userName like "%%%s%%";' %doctor_login_name
    try:
        stdin, stdout, stderr=exe_sql(allQunSql)
        AllUser=stdout.read()
        UserList=AllUser.split("\n")[1:-1]
        textqun.insert(tk.END,"%-15s%-13s%-20s%-25s%-50s" %("userName:","password:","name:","createTime:","hospital:"))
        for x in UserList:
            Duser=x.split("\t")
            textqun.insert(tk.END,"%-15s%-13s%-20s%-25s%-50s" %(Duser[0],Duser[1],Duser[2],Duser[4],Duser[3]))
        for i in range(len(UserList)+1):
            textqun.itemconfig(i,bg="#D3D3D3")
            if i%2==0:
                textqun.itemconfig(i,bg="#C0C0C0")
    except Exception as e:
        tkMessageBox.showinfo(title=' ',message=e)

def clear_text_area():
    listnum=textqun.size()
    if listnum==0:
        pass
    else:
        for i in range(listnum):
            textqun.delete(0)

def read_file_path(relative_path):
    #读取打包后的相对路径
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def login_to_ssh(ssh_ip,ssh_user,ssh_pwd=None,port=22):
    host=(ssh_ip,ssh_user,ssh_pwd)
    if host[1]=="ec2-user":
        PrivateKey=read_file_path("wisonic-cloud.pem")
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host[0],username=host[1],compress=True,key_filename=PrivateKey)
        except Exception as e:
            tkMessageBox.showinfo(title=' ',message=e)
            exit(0)
        return host,ssh
    else:
        ssh=paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host[0],port,host[1],host[2])
        return host,ssh

def build_ui():
    pass

if __name__=="__main__":
    #
    RELEASE=True
    if RELEASE:
        HOST_IP="ipaddr"
        HOST_USER="xxxx"
        host,ssh=login_to_ssh(HOST_IP,HOST_USER)
    else:
        HOST_IP="192.168.1.145"
        HOST_USER="xxxx"
        HOST_PWD='xxxx'
        host,ssh=login_to_ssh(HOST_IP,HOST_USER,HOST_PWD)
    #
    root=tk.Tk()
    root.resizable(False, False)
    FileName=u"移动医疗小工具2.2.5"
    root.title("%s work@'%s'" %(FileName,host[0]))
    root.geometry('610x280')
    #root.iconbitmap('wisonic.ico')
    #控件代码
    dhospital_lable=tk.Label(root,text=u"所属医院:")
    dhospital=tk.StringVar()
    dhospital_entry=tk.Entry(root,relief = 'solid',textvariable=dhospital)
    ddepartment_lable=tk.Label(root,text=u"所属科室:")
    ddepartment=tk.StringVar()
    ddepartment_entry=tk.Entry(root,relief = 'solid',textvariable=ddepartment)
    dposition_lable=tk.Label(root,text=u"职位:")
    dposition=tk.StringVar()
    dposition_entry=tk.Entry(root,relief = 'solid',textvariable=dposition)
    dname_lable=tk.Label(root,text=u"医生姓名:")
    dname=tk.StringVar()
    dname_entry=tk.Entry(root,relief = 'solid',textvariable=dname)
    dusername_lable=tk.Label(root,text=u"*医生账号:",fg="red")
    dusername=tk.StringVar()
    dusername_entry=tk.Entry(root,relief = 'solid',textvariable=dusername)
    dpwd_lable=tk.Label(root,text=u"*密码:",fg="red")
    dpwd=tk.StringVar()
    dpwd_entry=tk.Entry(root,relief = 'solid',textvariable=dpwd)
    Insert_button=tk.Button(root, width=10,heigh=1,fg="blue",relief="groove",text=u"添加",bg="Gainsboro",activebackground="grey",state="disabled",command=sql_insert)
    check_button=tk.Button(root, width=10,heigh=1,fg="blue",relief="groove",text=u"检查用户可用",bg="Gainsboro",activebackground="grey",command=account_check)
    #分割线
    Separator1 = ttk.Separator(root, orient=tk.VERTICAL)
    Separator2 = ttk.Separator(root, orient=tk.VERTICAL)
    #群创建
    qun_name_lable=tk.Label(root,text=u"*群名称：",fg="red")
    qun_name=tk.StringVar()
    qun_name_entry=tk.Entry(root,relief = 'solid',textvariable=qun_name)
    zuzhi_name_lable=tk.Label(root,text=u"组织名称：")
    zuzhi_name=tk.StringVar()
    zuzhi_name_entry=tk.Entry(root,relief = 'solid',textvariable=zuzhi_name)
    bumen_name_lable=tk.Label(root,text=u"部门名称：")
    bumen_name=tk.StringVar()
    bumen_name_entry=tk.Entry(root,relief = 'solid',textvariable=bumen_name)
    admin_name_lable=tk.Label(root,text=u"*群主账号：",fg="red")
    admin_name=tk.StringVar()
    admin_name_entry=tk.Entry(root,relief = 'solid',textvariable=admin_name)
    qun_button=tk.Button(root, width=10,heigh=1,relief="groove",fg="blue",bg="Gainsboro",activebackground="grey",text=u"创建群",command=create_qun)
    ShowAllQun_button=tk.Button(root, width=10,heigh=1,relief="groove",fg="blue",bg="Gainsboro",activebackground="grey",text=u"查看群",command=show_all_qun)
    ShowAllUser_button=tk.Button(root, width=10,heigh=1,relief="groove",fg="blue",bg="Gainsboro",activebackground="grey",text=u"查看用户信息",command=show_user_info)
    scrolly=tk.Scrollbar(root,relief="groove")
    textqun=tk.Listbox(root,height=6,width=80,relief="solid",yscrollcommand=scrolly.set)
    scrolly.config(command=textqun.yview)
    #布局代码
    dhospital_lable.grid(row=0,column=0,sticky=tk.E)
    dhospital_entry.grid(row=0,column=1)
    ddepartment_lable.grid(row=1,column=0,sticky=tk.E)
    ddepartment_entry.grid(row=1,column=1)
    dposition_lable.grid(row=2,column=0,sticky=tk.E)
    dposition_entry.grid(row=2,column=1)
    dname_lable.grid(row=3,column=0,sticky=tk.E)
    dname_entry.grid(row=3,column=1)
    dusername_lable.grid(row=4,column=0,sticky=tk.E)
    dusername_entry.grid(row=4,column=1)
    dpwd_lable.grid(row=5,column=0,sticky=tk.E)
    dpwd_entry.grid(row=5,column=1)
    Insert_button.grid(row=0,column=3,rowspan=2,sticky=tk.W+tk.E+tk.N+tk.S,padx=5, pady=5)
    check_button.grid(row=4,column=3,rowspan=2,sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
    #
    Separator1.grid(row=0,column=4,rowspan=7,sticky="ns")
    Separator2.grid(row=0,column=5,rowspan=7,sticky="ns")
    #
    qun_name_lable.grid(row=0,column=6,sticky=tk.E)
    qun_name_entry.grid(row=0,column=7)
    zuzhi_name_lable.grid(row=1,column=6,sticky=tk.E)
    zuzhi_name_entry.grid(row=1,column=7)
    bumen_name_lable.grid(row=2,column=6,sticky=tk.E)
    bumen_name_entry.grid(row=2,column=7)
    admin_name_lable.grid(row=3,column=6,sticky=tk.E)
    admin_name_entry.grid(row=3,column=7)
    qun_button.grid(row=2,column=8,rowspan=2,sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
    ShowAllQun_button.grid(row=5,column=8,rowspan=2,sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
    ShowAllUser_button.grid(row=5,column=7,rowspan=2,sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
    textqun.grid(row=8,column=1,columnspan=60)
    scrolly.grid(row=8,column=0)
    root.mainloop()
    ssh.close()
