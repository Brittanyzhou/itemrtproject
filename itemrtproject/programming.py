import os
import ntpath
import re
import subprocess
import datetime
from itemrtproject.settings import CODE_ROOT,COMPILER_PATH,EXECUTER_PATH
from itemrtdb.models import *
def get_java_class_name(code):
    pattern=re.compile('public\s+class\s+(.+){')
    if (pattern.search(code)):
        class_name=pattern.search(code).groups()[0]
        return class_name
    else:
        return None
class ProgramTester ():
    def __init__(self,code,user,question):
        self.code=code
        self.user=user
        self.question=question
        self.srcFileName=''
        self.compiledFileName=''
        self.mark=0
        self.work_dir=''
        self.result_brief=''
        self.result_detail=''

def get_work_dir(question,user):
    folder_relative_path=os.path.join("question",str(question.id),"submissions",str(user.id))
    work_dir=os.path.join(CODE_ROOT,folder_relative_path)
    return work_dir

def save_code(code,save_path):
    # 1 check code type
        # 1-1 get class name
    class_name=get_java_class_name(code=code)
    if (class_name):
        file_name=class_name + ".java"
    else:
        raise Exception("Java class name is not found")
    #2 save the file
    file_abs_path=os.path.join(save_path,file_name)
    try:
        with open(file_abs_path,mode='w') as f:
            f.write(code)
        return file_abs_path
    except Exception as e:
        raise Exception("Error occurred in saving the source code file")

def get_compiler_path():
    try:
        compiler_path=COMPILER_PATH
        return compiler_path
    except:
        raise Exception("get_compiler_path() error: the compiler path doesn't exist")

def _get_executer_path():
    try:
        executer_path=EXECUTER_PATH
        return executer_path
    except:
        raise Exception("_get_executer_path() error: the executer path doesn't exist")


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
        compiled_file_path=_get_compiled_file_path(src_file_path=src_file_path)
        return compiled_file_path

def _is_auto_run_test():
    # TODO: may set an suto-run-test settings in question model
    return AUTO_RUN_TEST


def _run_test_and_record(question,compiled_file_path,work_dir,question_submission):
    #1 get testcases
    test_cases=TestCase.objects.filter(question=question)
    number_of_test_cases=len(test_cases)
    number_of_passes=0
    overall_result_brief=''
    overall_result_detail=''
    mark=0
    #2 loop through testcases
    for test_case in test_cases:
        #2-1 get inputs
        test_input_list=test_case.test_inputs.splitlines()
        expected_output_list=test_case.expected_outputs.splitlines()
        #2-2 run the program
        #2-2-1 get executer path
        executer_path=_get_executer_path(question.required_language)
        #2-2-2 run the program
        if (question.required_language=='java'):
            base_compiled_file_name=ntpath.basename(compiled_file_path)
            proc=subprocess.Popen([executer_path,os.path.splitext(base_compiled_file_name)[0]],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=work_dir,shell=True)
        elif(question.required_language.upper()=='C'):
            proc=subprocess.Popen([compiled_file_path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=work_dir,shell=True)
        for test_input in test_input_list:
            proc.stdin.write('{}\n'.format(test_input))
        #2-2-3 get outputs and errors
        actual_output_list=proc.stdout.readlines()
        actual_error_list=proc.stderr.readlines()
        #2-3 compare outputs and get result
        is_pass,result_description=_analyze_result(test_errors=actual_error_list,test_inputs=test_input_list,actual_outputs=actual_output_list,expected_outputs=expected_output_list)
        #2-4 record number_of_pass
        if (is_pass):
            number_of_passes +=1
        overall_result_detail +='Test ' + test_case.title + ' result:<br/>'+result_description + '<br/>'
        #2-5 save to a test case result
        test_case_result=TestCaseResult.objects.create(
            result_detail=result_description,
            test_case=test_case,
            question_submission=question_submission,
            is_pass=is_pass
        )
        test_case_result.save()
    #3 get the overall result_brief
    overall_result_brief +='Total: ' + str(number_of_passes) +'tests out of '+ str(number_of_test_cases) + 'tests passed' +'<br/>'
    #4 get the score
    if (number_of_test_cases==number_of_passes):
        mark=100
    else:
        mark=number_of_passes/number_of_test_cases*100
    #5 change the mark for question submission
    question_submission.score=mark
    question_submission.save()
    #6 return the result string
    return overall_result_brief,overall_result_detail


def run_tester(code,task,question,user):
    #1 save the code to a file
    #1-1 set the directory to put the file
    work_dir=get_work_dir(task=task,question=question,user=user)
    #1-2 create the directory
    if not os.path.exists(work_dir):
       os.makedirs(work_dir)
    #1-3 save the code to a file
    required_language=question.required_language
    src_file_path=save_code(code=code,save_path=work_dir,code_type=required_language)

    #2 compile the code
    #2-1 get the compiler path
    compiler_path=get_compiler_path(language=required_language)
    #2-2 compile the src file
    compiled_file_path=_compile_src_file(compiler_path=compiler_path,
                                         src_file_path=src_file_path,
                                         work_dir=work_dir)
    #3 save question submission
    try:
        question_submission=QuestionSubmission.objects.create(
            question=question,
            submission_time=datetime.datetime.now(),
            score=0,
            src_file_path=src_file_path,
            compiled_file_path=compiled_file_path,
            submitted_by=user
        )
        question_submission.save()

    except Exception as e:
        raise Exception(e.message + "runtester() error: fail to save question_submission")
    #3-1 check whether needs to run test cases
    if (_is_auto_run_test()):
        _run_test_and_record(question=question,question_submission=question_submission,compiled_file_path=compiled_file_path,work_dir=work_dir)

    return question_submission