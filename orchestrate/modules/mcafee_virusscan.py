class action_class:
        def required_vars():
            my_vars=('host','policy')
            return my_vars

        def do_action(form,logging):
            import subprocess, requests
            o_username="user"
            o_password="123pass"

            try:
                host=form.getvalue('host')
                policy=form.getvalue('policy')
            except:
                print("Missing required value. Exiting.")
                exit()
            if(host is None) or (policy is None):
                print("Missing required value. Exiting.")
                exit()

            def sanitize(value,o_pass):
                output = str(value).replace(o_pass,'*******')
                return str(output)

            def safety_check(value):
                #if host in never_host list
                #if ip in never_ip list
                #if prohibited_chars in value
                #send alert action failed due to safety check

            print ("Killing " + pid + " on host " + host + "<br>")
            print ("Initiaiting viruscan policy " + policy + " on host " + host + "<br>")
            logging.info("Initiaiting viruscan policy " + policy + " on host " + host)


            try:
                ePO_server=''
                ePO_username=''
                ePO_password=''
                response = requests.post(url=ePO_server, data=data, auth=HTTPBasicAuth(ePO_username, ePO_password))
                ## curl -k -u '$user:$pass' 'https://server/remote/clienttask.run?names=$host&productId=ENDP_GS_1000&taskId=21'"
                result=response
                print("Result: "+str(result))
            except subprocess.CalledProcessError as e:
                print(sanitize(e,o_pass))
                print(sanitize(e.output,o_pass))
