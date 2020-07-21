class action_class:

 def required_vars():
     my_vars = ('host','pid')
     return my_vars

 def show_action(form):
    text = "Going to kill " + pid + " " + name + " on " +host
    return text

 def do_action(form):
    import subprocess
    import os
    import timestamp
    host=form.getvalue('host')
    pid=form.getvalue('pid')
    name=form.getvalue('name')
    log_prefix = str(timestamp.timestamp.now()) + " module:kill_process message:"

    if interactive:
        if form.getvalue("confirm") == True:
            print("Confirmed<br>")
        else:
            print("please confirm you want to kill process id on host")
            print("<form action="+uri+"><input type=hiddin name=confirm value=True><input type=submit></form>")
            exit()


    print("Killing " + pid + " " + name + " on " +host)
    logging.info(log_prefix + "Killing "+pid+" on " +host)

    try:
        user = str(subprocess.check_output("whoami",stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,shell=True))
    except:
        print("Couldnt get user")

    def sanitize(value):
        output = str(value).replace(o_pass,'******')
        return str(output)



    ## Userame may need domain prepended. domain\\username. use 2 \\ 
    o_username = "domain\\username"
    cmd_command = "taskkill /s "+host+" /pid "+pid+" /u "+o_username+" /p "+o_password + " "
    try:
        result = subprocess.check_output(cmd_command,stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,shell=True)
        print("<br>Result: " + str(result))
    except subprocess.CalledProcessError as e:
        print(sanitize(e))
        print(sanitize(e.output))
