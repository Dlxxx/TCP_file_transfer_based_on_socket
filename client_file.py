import socket
import threading
import os
from tkinter import *
from tkinter import scrolledtext
import time
import random
import hashlib
import json
# pip install tk if you're going to use

# Alert: This code has a terrible writing style
permit=True

def recv_data(sock, window):

    global permit

    while True:
        data = sock.recv(1024).decode('utf-8')
        if not data:
            break

        if data[:5] == 'FILE:':
            print('[Client] Begin to receive file...')
            print('[Client] ', data[5:])
            filename, filesize = data[5:].split('$')
            origin, extension = filename.split('.')
            filesize = int(filesize)
            newnameint = random.randint(1000000,9999999)
            newname = str(newnameint)
            # 保存路径
            newfile = 'D:\\Drug\\Computer_Net\\Codes\\Group\\Mine\\recv\\' + newname + '.' + extension
            with open(newfile, 'wb') as f:
                total_size = 0
                while total_size < filesize:
                    data = sock.recv(1024)
                    f.write(data)
                    total_size += len(data)
            print('[Client] File received.')
            window['state'] = 'normal'
            window.insert(INSERT, f'Succeeded receiving file: {filename}({filesize} bytes)')
            window.insert(INSERT, '\nFile saved in: ' + newfile)
            window['state'] = 'disabled'
        else:    
            print("New message:", data)
            window['state'] = 'normal'
            window.insert(INSERT, '>>>' + data)
            window['state'] = 'disabled'
            # new_text = Label(window, text=data)
            # new_text.pack(side='top')


def main():
    # Creating Socket and Connect to the Server
    server_ip = '10.0.1.2'
    server_port = 9037
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    Online = False

    # Making Graphical Interfaces
    window = Tk()
    window.title("Chat Window")
    window.geometry("800x500")
    # Label
    lbl_server = Label(window, text=client_socket.recv(1024).decode('utf-8'))
    lbl_server.place(x=310, y=0)
    lbl = Label(window, text="Please login or sign up")
    lbl.place(x=310, y=30)
    lbl_username = Label(window, text="Username: ")
    lbl_username.place(x=290, y=70)
    lbl_password = Label(window, text="Password: ")
    lbl_password.place(x=290, y=110)
    # Entry
    txt_username = Entry(window, width=20)
    txt_username.place(x=390, y=70)
    txt_password = Entry(window, width=20)
    txt_password.place(x=390, y=110)
    # Button
    # Making new screens
    def OnlineScreen():
        global permit
        # Making Chat Displaying Screen
        display = scrolledtext.ScrolledText(window, bg='lightblue', state='disabled')
        display.place(width=750, height=380, x=20, y=10)
        # Receiving Messages
        t = threading.Thread(target=recv_data, args=(client_socket,display))
        t.start()
        # t.join()
        # Sending Messages
        message = scrolledtext.ScrolledText(window)
        message.place(width=600, height=100, x=10, y=340)
        
        def SendMessage():
            data = message.get(1.0, END)
            data_ty = 'MSNG:' + data
            display['state'] = 'normal'
            display.insert(INSERT, 'Me: '+data)
            display['state'] = 'disabled'
            if client_socket.send(data.encode('utf-8')) :
                print("A message has been sent successfully: ", data.encode('utf-8'))
            message.delete(1.0, END)
            
        def TransmitFile():
            print("ready to get message")
            filename = message.get(1.0, END)[:-1]
            print('Ready to send file: ', filename)
            filesize = os.path.getsize(filename)
            print('Get file size: ', filesize)
            filesize_msg = f'FILE:{filename}${filesize}'.encode('utf-8')
            client_socket.send(filesize_msg)
            with open(filename, 'rb') as f:
                while True:
                    print(1)
                    filedata = f.read(1024)
                    if not filedata:
                        break
                    client_socket.send(filedata)
            display['state'] = 'normal'
            display.insert(INSERT, f'Succeeded sending file: {filename}({filesize} bytes)\n')
            display['state'] = 'disabled'
            message.delete(1.0, END)
            
        def UploadFile():
            global permit
            permit=False
            def print_bar(percent):
                bar = '\r' + '*' * int((percent * 100)) + ' %3.0f%%|' % (percent*100) + '100%'
                print(bar, end = '', flush = True)
            file_path = message.get(1.0, END)[:-1]
            if len(file_path) == 0: 
                permit=True
                return
            file_size = os.path.getsize(file_path)
            info=f'UPLOAD:{file_path}${file_size}'.encode('utf-8')
            client_socket.send(info)
            time.sleep(0.2)
            file_seek = 0
            new_size = file_size - file_seek
            begin_size = new_size
            with open(file_path, "rb") as f:
                f.seek(file_seek)
                while new_size:
                    content = f.read(1024)
                    client_socket.send(content)
                    new_size -= len(content)
                    print_bar(round((begin_size - new_size) / begin_size, 2))
                    # time.sleep(0.2)
                print("")
            permit=True
            display['state'] = 'normal'
            display.insert(INSERT, f'Succeeded uploading file: {file_path}({file_size} bytes)\n')
            display['state'] = 'disabled'
            message.delete(1.0, END)
            
        def DownloadFile():
            global permit
            permit=False
            file_path = message.get(1.0, END)[:-1]
            if len(file_path) == 0: 
                permit=True
                return
            file_size = os.path.getsize(file_path)
            info=f'DOWNLOAD:{file_path}${file_size}'.encode('utf-8')
            client_socket.send(info)
            time.sleep(0.2)
            state_message = client_socket.recv(1024).decode("utf-8")
            print(state_message)
            client_socket.send("Got state.".encode("utf-8"))
                
            if(state_message == "1"):
                server_response = client_socket.recv(1024)
                file_size = int(server_response.decode("utf-8"))
                print("Expected total size is ", file_size)
                
                client_socket.send("ready to receive".encode("utf-8"))
                
                name = os.path.basename(file_path)
                new_file_name = file_path.replace(name, '') +"Download_" + name
                file_size = os.path.getsize(file_path)

                f = open(new_file_name, "wb")
                received_size = 0
                m = hashlib.md5()
        
                while received_size < file_size:
                    size = 0
                    if file_size - received_size > 1024:
                        size = 1024
                    else:
                        size = file_size - received_size
                    data = client_socket.recv(size)
                    data_len = len(data)
                    received_size += data_len
                    percent = (received_size*1.0)/file_size*100.0
                    print("ALREADY received: ", f'{percent:.4f}', "%")
                    m.update(data)
                    f.write(data)
                f.close()
                print("Actual received size: ", received_size)
                md5_server = client_socket.recv(1024).decode("utf-8")
                md5_client = m.hexdigest()
                print("md5 sent by the server: ", md5_server)
                print("md5 sent by the client: ", md5_client)
                if md5_server == md5_client:
                    print("md5 is checked correctly")
                else:
                    print("md5 checked WRONG!")
            permit=True
            display['state'] = 'normal'
            display.insert(INSERT, f'Succeeded uploading file: {file_path}({file_size} bytes)\n')
            display['state'] = 'disabled'
            message.delete(1.0, END)
                    
        btn_send = Button(window, text="Send", command=SendMessage)
        btn_send.place(x=680, y=340)
        
        btn_transmit = Button(window, text="Transmit", command=TransmitFile)
        btn_transmit.place(x=680, y=380)
        
        btn_upload = Button(window, text="Upload", command=UploadFile)
        btn_upload.place(x=680, y=420)
        
        btn_download = Button(window, text="Download", command=DownloadFile)
        btn_download.place(x=680, y=460)


    # Login
    def Login():
        username = txt_username.get()
        password = txt_password.get()
        client_socket.send(f'{username}:{password}'.encode('utf-8'))
        data = client_socket.recv(1024).decode('utf-8')
        if data == 'Succeed!':
            Online = True
            lbl.destroy()
            lbl_server.destroy()
            lbl_username.destroy()
            lbl_password.destroy()
            txt_username.destroy()
            txt_password.destroy()
            btn_login.destroy()
            btn_signup.destroy()
            OnlineScreen()
        else:
            lbl.configure(data)
    def Signup():
        return
    btn_login = Button(window, text="Login", command=Login)
    btn_login.place(x=355, y=200)
    btn_signup = Button(window, text="Sign up", command=Signup)
    btn_signup.place(x=410, y=200)
    window.mainloop()


    # Close
    client_socket.close()


if __name__ == '__main__':
    main()
