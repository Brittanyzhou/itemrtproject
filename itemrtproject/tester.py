import os
import ntpath
import re
import subprocess
import datetime
from itemrtproject.settings import CODE_ROOT,COMPILER_PATH,EXECUTER_PATH
from itemrtdb.models import *
from django.utils.encoding import smart_str, smart_unicode
#from assignment.models import Assignment,AssignmentQuestionSubmission
#from onlinetest.models import OnlineTest,OnlineTestQuestionSubmission
AUTO_RUN_TEST=True
S=""
C=""
def get_java_class_name(code):
    pattern=re.compile('public\s+class\s+(.+){')
    if (pattern.search(code)):
        class_name=pattern.search(code).groups()[0]
        return class_name
    else:
        return None
def analyze_result(actual_outputs,expected_outputs,test_inputs,test_errors):
    result='' # for storing the detailed test result
    isPass=True
    expected_output_count=len(expected_outputs)
    actual_outputs_count=len(actual_outputs)

    result += "Test input : <br>"
    # add test inputs
    for item in test_inputs:
        result +=item + "<br>"

    for i in range(min(expected_output_count,actual_outputs_count)):
        current_expected_output=expected_outputs[i]
        current_actual_output=actual_outputs[i]

        result += "Expected output [" + str(i) + "] : " + current_expected_output + " ; Actual output [" + str(i) + "] : " + current_actual_output + "<br>"
        if (current_expected_output== current_actual_output.rstrip()):
            result +="Output [" + str(i) + "] is correct" + "<br>"
        else:
            result +="Output [" + str(i) + "] is wrong" + "<br>"
            isPass=False
    # for remaining unchecked output
    if (expected_output_count>actual_outputs_count):
        isPass=False
        # print the missing expected outputs
        for i in range(actual_outputs_count,expected_output_count):
            result +="Missing expected output:" + expected_outputs[i] + "<br>"
    elif (expected_output_count<actual_outputs_count):
        isPass=False
        # print the unexpected outputs
        for i in range(expected_output_count,actual_outputs_count):
            result +="Unexpected output:" + actual_outputs[i] + "<br>"

    # add error messages if any
    if (test_errors):
        result +="Errors occurred in runtime:" + "<br>"
        for item in test_errors:
            result +=item + "<br>"

    return isPass,result
def get_compiler_path():
    try:
        compiler_path=COMPILER_PATH
        return compiler_path
    except:
        raise Exception("get_compiler_path() error: the compiler path doesn't exist")
def _get_compiled_file_path(src_file_path):
    try:
        file_name, file_extension = os.path.splitext(src_file_path)
    except:
        raise Exception("_get_compiled_file_path() error, src_file_path="+src_file_path + " ; not a valid path")

    if(file_extension=='.java'):
        return file_name + '.class'
    else:
        raise Exception("_get_compiled_file_path() error, src_file_path="+src_file_path +" ; not supported type")
def _compile_src_file(compiler_path,src_file_path,work_dir):
    proc=subprocess.Popen([compiler_path,src_file_path],stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE,cwd=work_dir)
    out,err=proc.communicate()
    # if there is error, stops at current page
    if (err):
        raise Exception("Compilation Error: " + repr(err))
    else:
        #global C
        compiled_file_path=_get_compiled_file_path(src_file_path=src_file_path)
        #C=compiled_file_path
        return compiled_file_path
def _run_class_file(compiler_path,src_file_path,work_dir):
     proc=subprocess.Popen([compiler_path,src_file_path,work_dir],stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE,cwd=work_dir,shell=True)
     out,err=proc.communicate()
     if (err):
        raise Exception("Compilation Error: " + repr(err))
     else:
        compiled_file_path=_get_compiled_file_path(src_file_path=src_file_path)
        return compiled_file_path
class Programtest ():
 def __init__(self,code,user,question):
        self.code=code
        self.user=user
        self.question=question
        self.srcFileName=''
        self.fo=''
        self.compiledFileName=''
        self.mark=0
        self.work_dir=''
        self.result_brief=''
        self.result_detail=''
        self.src_file_path=''
 def compile(self):
        folder_name=str(self.user.id) + "-" + str(self.question.id)
        self.work_dir=os.path.join(CODE_ROOT,folder_name,)
        global S
        ss=self.work_dir
        S=self.work_dir
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
            # determine the src file name
            global C
        class_name=get_java_class_name(code=self.code)
        C=class_name
        if (class_name):
            src_file_name=class_name+".java"
        else:
            raise Exception("Can not find the java class name")
            # save the code to a src file
        try:
            with open(os.path.join(self.work_dir,src_file_name),"wb") as f:
                    f.write(self.code)
        except Exception as e:
                raise Exception("Error occured when saving the code to compile")
        #compiler_path= get_compiler_path()
        #s=_get_compiled_file_path( src_file_name)
        _compile_src_file('C:/Program Files (x86)/Java/jdk1.8.0_40/bin/javac.exe',src_file_name,ss)
        #self.compiledFileName=class_name+".class"
        #global C
        #self.compiledFileName=folder_name+"."+C
        self.compiledFileName=C
 @property
 def run_test(self):
        # load tests
        global S
        cc=S
        tests=ProgramCase.objects.filter(question=self.question)
        #result=ProgramResult.objects.all.get()(id=result.actual_output_list)
        number_of_passed_test=0
        number_of_failed_test=0
        self.mark=0
        mark_per_test=100/len(tests)
        # run through the tests
        for test in tests:
            #proc=subprocess.Popen(['C:/Program Files (x86)/Java/jdk1.8.0_40/bin/java.exe', self.compiledFileName],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=self.work_dir,shell=True)
            proc=subprocess.Popen(['C:/Program Files (x86)/Java/jdk1.8.0_40/bin/java.exe',self.compiledFileName,cc],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=self.work_dir,shell=True)
            #_run_class_file('C:/Program Files (x86)/Java/jdk1.8.0_40/bin/java.exe',self.compiledFileName,cc)
            current_test_input=test.programming_inputs
            input_lines=current_test_input.splitlines()
            for item in input_lines:
                #proc.stdin.write(format(item))
                proc.stdin.write('{}\n'.format(item))
            #proc.stdin.write('20\n')
                #print proc.stdout.read()
                #proc.stdin.close()
                #proc.stdin.write(item)
                #out=proc.stdout.readlines()
                #err=proc.stdout.readlines()
                #out,err=proc.communicate()
                #actual_output=out
                #actual_error=err
                #actual_output=proc.communicate()
                #actual_error=proc.communicate()[0]
                actual_output=proc.stdout.readlines()
                #actual_output=proc.communicate()[0]
                actual_error=proc.stderr.readlines()
               # get the result detail & brief
                isPass,current_test_result=analyze_result(actual_outputs=actual_output,expected_outputs=test.expected_outputs.splitlines(),test_inputs=input_lines,test_errors=actual_error)

            if (isPass):
                self.mark +=mark_per_test
                self.result_detail +='Test ' + test.result_detail + ' result:<br/>'+current_test_result + '<br/>'
                number_of_passed_test +=1
                #result.actual_output_list +='Test ' + test.description + ' result:<br/>'+current_test_result + '<br/>'
                #number_of_passed_test +=1
            else:
                self.result_detail +='Test ' + test.result_detail + ' result:<br/>'+current_test_result + '<br/>'
                number_of_failed_test +=1


        self.result_detail +='Total: ' + str(number_of_passed_test) + ' passed, ' + str(number_of_failed_test) + ' failed' + '<br/>'
        # self.result_brief +='Total score:' + str(self.mark)
        self.result_detail+='Total: ' + str(number_of_passed_test) + ' passed, ' + str(number_of_failed_test) + ' failed' + '<br/>'
        # self.result_detail +='Total score:' + str(self.mark)
        return self.result_brief,self.result_detail

def save_result(self):
        # create a new submission
        submission=AssignmentSubmission.objects.create(assignment=self.assignment,submitter=self.user,codeFilePath='',submittedTime=datetime.datetime.now())
        if (self.assignment.requiredLanguage=='java'):
            codeFileName=self.compiledFileName + '.java'
            submission.codeFilePath=os.path.join(self.work_dir,codeFileName)
        else:
            pass
            # TODO: add support for other languages
        submission.save()
        # create a assignment result
        assResult=AssignmentResult.objects.create(assignmentSubmission=submission,
                                                  mark=self.mark,
                                                  resultBrief=self.result_brief,
                                                  resultDetail=self.result_detail,
                                                  )
        assResult.save()
