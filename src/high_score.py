# Complete project details at https://RandomNerdTutorials.com
try:
  import usocket as socket
except:
  import socket


def web_page(score_table):
  if True:
    gpio_state="NEW GAME"
  else:
    gpio_state="EXIT"
  
  html = """
  <html>
  <head>
  <title>HIGH SCORE - TETRIS</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
  html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}
  p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}
  </style>
  </head>
  <body> 
  <h1>HIGH SCORE - TETRIS</h1> 
  <p>HIGHSCORE</p>
  <table border="10">
  <tr style="text-align: center"></tr>     

<table width="100%" bgcolor="bround" border="3" cellpadding="5" align="right" bordercolor="black">
 <tr align="left" bgcolor="red" valign="bottom">
 <td nowrap colspan="3" width="100"> <h3>HIGHSCORE</h2> </td>
 </tr>
<tr>
    <td><h3>DATE</h3></td>
   <td><h3>NAME</h3></td>
   <td><h3>SCORE</h3></td>
</tr>
<tr>
    <td>""" + str(score_table[0][0])+ """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + score_table[0][1] + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + str(score_table[0][2]) + """&nbsp;&nbsp;&nbsp;</td>
</tr>
<tr>
    <td>""" + str(score_table[1][0]) + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + score_table[1][1] + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + str(score_table[1][2]) + """&nbsp;&nbsp;&nbsp;</td>
</tr>
<tr>
     <td>""" + str(score_table[2][0]) + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + score_table[2][1] + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + str(score_table[2][2]) + """&nbsp;&nbsp;&nbsp;</td>
</tr>
<tr>
      <td>""" + str(score_table[3][0]) + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + score_table[3][1] + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + str(score_table[3][2]) + """&nbsp;&nbsp;&nbsp;</td>
</tr>
<tr>
    <td>""" + str(score_table[4][0]) + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + score_table[4][1] + """&nbsp;&nbsp;&nbsp;</td>
    <td>""" + str(score_table[4][2]) + """&nbsp;&nbsp;&nbsp;</td>
</tr>
</table>
<tr>
    <td>&nbsp;&nbsp;&nbsp;</td>
    <td>&nbsp;&nbsp;&nbsp;</td>
    <td>&nbsp;&nbsp;&nbsp;</td>
</tr>
  <!--<p> GPIO state: <strong>""" + gpio_state + """</strong> </p>-->
  <p><a href="/?led=on"><button class="button">NEW GAME</button></a></p>
  <p><a href="/?led=off"><button class="button button2">EXIT</button></a></p>
  </body>
  </html>"""

  return html

def set_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)



def Page_refresh(s, score_table):
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    request = str(request)

    led_on = request.find('/?led=on')
    led_off = request.find('/?led=off')
    exit = False
    if led_on == 6:
        print('LED ON')
    if led_off == 6:
        print('LED OFF')
        exit = True
        

    response = web_page(score_table)
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)

    conn.close()
    return exit