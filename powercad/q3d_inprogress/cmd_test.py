from cmd import Cmd

class MyPrompt(Cmd):

    def do_hello(self, args):
        """Says hello. If you provide a name, it will greet you with it."""
        if len(args) == 0:
            name = 'stranger'
        else:
            name = args
        print "Hello, %s" % name

    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit
    
    def do_nothing(self,args):
       print "you will be stuck" 
    def do_makf(self,args):
        "makefile [String] [Directory] " 
        "put a string in a file to a directory"
        f=open('newfile.txt','w')
        f.write(args[0])
        f.close()
            
if __name__ == '__main__':
    prompt = MyPrompt()
    prompt.prompt = '> '
    prompt.cmdloop('Starting prompt...')