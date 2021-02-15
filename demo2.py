#!/usr/bin/env python3

# Written by Chengxin Yu @ Feb 12, 2021
# SSL Fault Table Generator.
# Type in digital rules for the ciruit in the file called 'rules'.
# Only simulates for simple digital logic. Complex logic like gate fault in cmos structure is not supported yet.

# View Setting
USE_XV = 0
USE_X = 1

# read rules
rule_fileName = "rules"
rules = open(rule_fileName, "r")
inputs = []
wires = []
outputs = []
logics = []

faultInfoLst = {}
testVecInfoLst = []

subIn = 0
subOut = 0
subLog = 0
subWire = 0

for lines in rules:
    line = lines.rstrip() 
    
    if not line: # escape the empty lines
        continue   

    if 'inputs' in line:
        subIn = 1
        subOut = 0
        subLog = 0
        subWire = 0
        continue 
    
    if 'wires' in line:
        subWire = 1
        subOut = 0
        subIn = 0
        subLog = 0
        continue

    if 'outputs' in line:
        subOut = 1
        subIn = 0
        subLog = 0
        subWire = 0
        continue

    if 'logics' in line:
        subLog = 1
        subOut = 0
        subIn = 0
        subWire = 0
        continue
        
    if (subIn == 1):
        inputs += line.split()
    if (subWire == 1):
        wires += line.split()
    if (subOut == 1):
        outputs += line.split()
    if (subLog == 1):
        logics.append(line)
    
rules.close()

# print("inputs:  ", inputs)
# print("wires:   ", wires)
# print("outputs: ", outputs)
# print("logics:  ", logics)

inputNum = len(inputs)
wireNum = len(wires)
outputNum = len(outputs)

# total ssl faults
ssl_num = inputNum + outputNum + wireNum
total_ssl_num = 2*ssl_num

# ssl fault name
ssl_vars = inputs + wires +  outputs
# print("total SSL fault: ", total_ssl_num)

ssl_Str = []
for fault_var in ssl_vars:
    ssl_Str.append(fault_var + '/0')
    ssl_Str.append(fault_var + '/1')

# print("SSL cases: ", ssl_Str)
    
for fault in ssl_Str:
    faultInfoLst[fault] = []


testVectorNum = 2 ** inputNum
# print("total test num: ", testVectorNum)

formatStr = '#0{}b'.format(inputNum+2)

testVectors = []
for decNum in range(testVectorNum):
    testVector = tuple(int(i) for i in format(decNum, formatStr)[2:])
    testVectors.append(testVector)

# print(testVectors)

# inputVarStr = ''
# inputVarStr = " = 0\n".join(inputs)
# inputVarStr += ' = 0'
# print(inputVarStr)

# origFxStr = ''
# origFxStr = "\n".join(logics)
# print(origFxStr)

# loopStr = 'for testVector in testVectors:\n'
# loopStr += '\t{} = testVector\n'.format(','.join(inputs))
# loopStr += '\t{}\n'.format('\n\t'.join(logics))
# loopStr += '\tprint({})'.format(','.join(inputs))
# print(loopStr)

# print()


# exec(loopStr)
for output in outputs:
    print("FAULT TABLE FOR OUTPUT {}".format(output))
    print('{} | {} | '.format(' '.join(inputs), ' | '.join(output)), end='')
    print('{}'.format(' | '.join(ssl_Str)), end=' |\n')
    
    for testVector in testVectors:
        print('{} | '.format(' '.join([str(i) for i in testVector])), end='')
        for inVar in inputs:
            exec("{} = testVector".format(','.join(inputs)))
                
        for logic in logics:
            exec(logic)
            
        exec("{0}_orig = {0}".format(output))
            
        exec("print(int({}) ,'| ', end='')".format(", '|', ".join(output)))
        
        for ssl_fault in ssl_Str:
            # print(ssl_fault)
            exec("{} = testVector".format(','.join(inputs)))
            for inVar in inputs:
                if (inVar in ssl_fault):
                    # print('{}={}'.format(inVar,ssl_fault[-1]))
                    exec('{}={}'.format(inVar,ssl_fault[-1]))

            for logic in logics:
                wireVar = logic.split(' ')[0]
                if(wireVar in ssl_fault):
                    # print('{}={}'.format(wireVar,ssl_fault[-1]))
                    exec('{}={}'.format(wireVar,ssl_fault[-1]))
                else:
                    # print(logic)
                    exec(logic)
    
            # fault detection area
            fault = eval("{0} != {0}_orig".format(''.join(output)))
            
            if(USE_XV):
                # exec("if {0} != {0}_orig: print('x/{{}} | '.format({0}), end='')\nelse: print('  - | ', end='')".format(''.join(output)))
                if not fault:
                    print(' -  | ', end='')
                else:
                    exec("print('x/int({{}}) | '.format({0}), end='')".format(''.join(output)))
            elif (USE_X):
                # exec("if {0} != {0}_orig: print(' x  | '.format({0}), end='')\nelse: print(' -  | ', end='')".format(''.join(output)))
                if not fault:
                    print(' -  | ', end='')
                else:
                    print(' x  | ', end='')
            else:
                exec("print( ' int({{}})  | '.format({}), end='')".format("".join(output))) # print result
        print()
        
print()
print("FAULT TABLE IN GENERAL")
print('{} | '.format(' '.join(inputs)), end='')
print('{}'.format(' | '.join(ssl_Str)), end=' |\n')


test_idx = 0
for testVector in testVectors:
    testVecInfoLst.append({"test vector": testVector, "detect faults": []})
    
    print('{} | '.format(' '.join([str(i) for i in testVector])), end='')
        
    for inVar in inputs:
        exec("{} = testVector".format(','.join(inputs)))
            
    for logic in logics:
        exec(logic)

    for output in outputs:            
        exec("{0}_orig = {0}".format(output))
    
    for ssl_fault in ssl_Str:
        exec("{} = testVector".format(','.join(inputs)))
        for inVar in inputs:
            if (inVar in ssl_fault):
                # print('{}={}'.format(inVar,ssl_fault[-1]))
                exec('{}={}'.format(inVar,ssl_fault[-1]))

        for logic in logics:
            wireVar = logic.split(' ')[0]
            if(wireVar in ssl_fault):
                # print('{}={}'.format(wireVar,ssl_fault[-1]))
                exec('{}={}'.format(wireVar,ssl_fault[-1]))
            else:
                # print(logic)
                exec(logic)
        
        # fault detection area
        for output in outputs:
            fault = eval("{0} != {0}_orig".format(''.join(output)))
            if fault:   # fault detected
                faultInfoLst[ssl_fault].append(testVector)
                
                testVecInfoLst[test_idx]["detect faults"].append(ssl_fault)
                break
        if not fault:
            print(' -  | ', end='')
        else:
            print(' x  | ', end='')     
    print()
    test_idx += 1

# for faultInfo in faultInfoLst:    
#     print(faultInfo, faultInfoLst[faultInfo])
    
    
print() 

# for testVector in testVecInfoLst:    
#     print(testVector)

pre_EqFaultInfo_Dic = {} # this provides fault groups that need same amount of test vectors

for fault_name in faultInfoLst:
    if (str(len(faultInfoLst[fault_name])) not in pre_EqFaultInfo_Dic ):
        pre_EqFaultInfo_Dic[str(len(faultInfoLst[fault_name]))] = []
        pre_EqFaultInfo_Dic[str(len(faultInfoLst[fault_name]))].append((fault_name))
    else:
        pre_EqFaultInfo_Dic[str(len(faultInfoLst[fault_name]))].append((fault_name))
        
# for faultLen in pre_EqFaultInfo_Dic:
#     print(faultLen, pre_EqFaultInfo_Dic[faultLen])


EqFaultInfo_Dic = {}    # the equivalent set !!!!!!!!! not correct ！！！

for faultlen in pre_EqFaultInfo_Dic:
    testVecNum = len(pre_EqFaultInfo_Dic[faultlen])
    tmp_EqFaultInfo_Dic = {}
    for idx in range(testVecNum):
        fault_name = pre_EqFaultInfo_Dic[faultlen][idx]
        for cmp_idx in range(testVecNum-idx):
            cmp_fault_name = pre_EqFaultInfo_Dic[faultlen][cmp_idx + idx]
            if (faultInfoLst[cmp_fault_name] == faultInfoLst[fault_name]):
                # print("equivalent: {}, {}".format(fault_name, cmp_fault_name))
                if(str(faultInfoLst[cmp_fault_name]) not in tmp_EqFaultInfo_Dic):
                    tmp_EqFaultInfo_Dic[str(faultInfoLst[cmp_fault_name])] = []
                    tmp_EqFaultInfo_Dic[str(faultInfoLst[cmp_fault_name])].append(cmp_fault_name)
                else:
                    if(cmp_fault_name not in tmp_EqFaultInfo_Dic[str(faultInfoLst[cmp_fault_name])]):
                        tmp_EqFaultInfo_Dic[str(faultInfoLst[cmp_fault_name])].append(cmp_fault_name)
    # print(tmp_EqFaultInfo_Dic)
    EqFaultInfo_Dic[faultlen] = []                    
    for key in tmp_EqFaultInfo_Dic:
        EqFaultInfo_Dic[faultlen].append(tmp_EqFaultInfo_Dic[key])

print("EQUIVALENT FAULT SETS")
for faultLen in EqFaultInfo_Dic:
    # print(EqFaultInfo_Dic[faultLen]) 
    for sublst in EqFaultInfo_Dic[faultLen]:
        print(sublst)