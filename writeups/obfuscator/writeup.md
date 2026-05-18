# Obfuscator writeup

when we run the [obfuscator](/obfuscator/obfuscator) we see that it requires a second argument which is the password 

we run strings as usual and we notice anti debuggers

![strings](/obfuscator/pictures/Screenshot_20260512_141631.png)

we can notice the ptrace and some other anti-debugging techniques like pidtrace and parent process name check