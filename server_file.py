import socket
import threading
import os
import hashlib
# Alert: This code has a terrible writing style


def handle_client(client_socket, client_addr, clients):

    # 向客户端发送欢迎消息
    client_socket.send(f'Connected to server successfully'.encode('utf-8'))

    # 验证用户身份
    while True:
        # 接收客户端发送的用户名和密码
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            break
        username, password = data.split(':')
        if username == 'admin' and password == '123456':
            # 将客户端加入到在线列表中
            clients[client_addr] = client_socket
            client_socket.send(f'Succeed!'.encode('utf-8'))
            break
        else:
            client_socket.send(f'login fail. Please try again: '.encode('utf-8'))

    # 如果用户验证成功，则开始接收客户端发送的消息并转发给其他客户端
    
    
    while True:
        data = client_socket.recv(1024)
        # print(eval(data.decode()))
        if len(data)==0:
            break
        # 正常文件传输
        elif data[:5].decode('utf-8') == 'FILE:':
            while(len(data)):
                for addr, sock in clients.items():
                    if addr != client_addr:
                        sock.send(data)
                data = client_socket.recv(1024)
        
        elif data[:7].decode('utf-8') == 'UPLOAD:':
            try:
                connected = True
                print(data[7:].decode('utf-8'))
                filename, filesize = data[7:].decode('utf-8').split('$')
                print('checkpoint 2')
                origin, extension = filename.split('.')
                file_path=origin+"_upload."+extension
                filesize = int(filesize)   
                file_seek=0         
                if os.path.exists(file_path):
                    print("File Exists!")
                new_size = filesize - file_seek
                with open (file_path, "ab") as f:
                    while new_size:
                        content = client_socket.recv(1024)
                        f.write(content)
                        new_size -= len(content)
                        if content == b'':
                            connected = False
                            break
                if not connected :
                    print("Opps...Client is OUT!")
            except Exception as e:
                print("Error: ", str(e))
                break       

        elif data[:9].decode('utf-8') == 'DOWNLOAD:':
            try:
                file_path, filesize = data[9:].decode('utf-8').split('$')
                if not file_path:
                    print("Opps...Not valid path!")
                    break
                print("target path received: ", file_path)
                
                file_name = os.path.basename(file_path)
                print("target file is ",file_name, " ", type(file_name))

                if os.path.exists(file_path): #?
                    state = "1"
                    print("sign: ", state)
                    client_socket.send(state.encode("utf-8"))
                    client_socket.recv(1024)
                    
                # 1st send the file size, alarm the client
                    size = os.stat(file_path).st_size #?
                    client_socket.send(str(size).encode("utf-8"))
                    print("File Size been sent: ", size)

                # 2nd send the content
                    client_socket.recv(1024)
                    m = hashlib.md5()
                    f = open(file_path, "rb")
                    for line in f:
                        client_socket.send(line)
                        m.update(line)
                    f.close()

                    # 3rd send md5
                    md5 = m.hexdigest()
                    client_socket.send(md5.encode("utf-8"))
                    print("md5: ", md5)
                else:
                    state = "0"
                    client_socket.send(state.encode("utf-8"))
                    print("Ready to perform...")

            except Exception as e:
                print("Error arose ", str(e))
                break
        else:# 一般文字信息
            while(len(data)):
                for addr, sock in clients.items():
                    if addr != client_addr:
                        sock.send(data)
                data = client_socket.recv(1024)

    # 断开连接
    client_socket.close()
    del clients[client_addr]
    print(f'Server{client_addr}Disappear')

def main():
    # 创建socket对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定本地IP和端口
    HOST = '10.0.1.2'
    PORT = 9037
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    # 在线客户端列表
    clients = {}

    print('waiting for client...')

    while True:
        # 接受客户端连接请求
        client_socket, client_addr = server_socket.accept()
        print(f'client{client_addr}connect successful')

        # 使用线程处理客户端请求
        t = threading.Thread(target=handle_client, args=(client_socket, client_addr, clients))
        t.start()

    # 关闭socket
    server_socket.close()

if __name__ == '__main__':
    main()


