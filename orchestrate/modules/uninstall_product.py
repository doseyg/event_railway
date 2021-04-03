class action_class:
        def required_vars():
            my_vars=('host','product')
            return my_vars

        def do_action(form,logging):
            import subprocess, os
            o_username="user"
            o_password="123pass"

            try:
                host=form.getvalue('host')
                name=form.getvalue('product')
            except:
                print("Missing required value. Exiting.")
                exit()
            if(host is None) or (product is None):
                print("Missing required value. Exiting.")
                exit()

            def sanitize(value,o_pass):
                output = str(value).replace(o_pass,'*******')
                return str(output)

            def safety_check(value):
                #if host in never_host list
                #if product in never_product list
                #if ip in never_ip list
                #if prohibited_chars in value
                #send alert action failed due to safety check

            print ("Killing " + pid + " on host " + host + "<br>")
            print ("Uninstalling " + product + " on host " + host + "<br>")
            logging.info("Uninstalling " + product + " on host " + host)
            ps_command = "powershell.exe -executionPolicy bypass"
            cmd_command = "taskkill.exe /s " + host + " /IM " + name + " /u " + o_username + " /p " + o_pass + " "
            wmi_command = "wmic /NODE:"+ host+" /USER "+o_username+" /PASS "+o_pass+" product name=\""+product+"\" call uninstall"

            try:
                result = subprocess.check_output(cmd_command,stdin=subprocess.DEVNULL,stderr=subprocess.STDOUT,shell=True)
                print("Result: "+str(result))
            except subprocess.CalledProcessError as e:
                print(sanitize(e,o_pass))
                print(sanitize(e.output,o_pass))
