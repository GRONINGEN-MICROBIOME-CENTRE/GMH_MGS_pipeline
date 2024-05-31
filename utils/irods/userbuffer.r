usedbuffer {
   msiExecCmd(*Cmd,*Arg,"irs01","null","null",*Result);
   msiGetStdoutInExecCmdOut(*Result,*Out);
   writeLine("stdout","iDAS buffer filesystem used space");
   writeLine("stdout","*Out");
}
INPUT *Cmd="usedbuffer"
OUTPUT ruleExecOut
