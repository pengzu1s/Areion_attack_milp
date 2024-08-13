import os
import gurobipy as gp
from gurobipy import GRB

XOR_RULE = [[-1,-1,-1,0,0,-3,0,-1,3,2,1,3],
[-1,-1,3,0,-2,2,1,2,-2,-4,-2,2],
[-1,-1,2,-2,0,1,2,1,-1,-1,-4,2],
[1,0,0,0,-1,-1,0,0,-1,0,-1,2],
[1,1,1,-1,0,-1,0,0,-2,-2,0,2],
[1,2,1,1,2,1,-3,-2,-3,2,0,1],
[-1,0,-1,1,1,1,1,-1,-2,1,-3,2],
[-3,0,-3,-2,-2,-2,3,0,1,0,-4,6],
[0,-3,-3,-2,-2,-2,0,3,1,-3,-1,6],
[0,0,-3,-1,-1,-1,-1,0,3,1,2,3],
[0,0,0,1,0,0,-1,0,0,0,1,0],
[1,0,1,-1,0,0,-1,0,0,0,0,1],
[0,0,0,0,1,0,0,-1,0,1,0,0],
[0,1,0,0,0,0,0,-1,0,1,0,0],
[0,0,0,1,1,1,0,0,0,-1,0,0]]

SBOX_RULE = [[0,-2,-1,0,1,0,1],
[-2,0,-1,1,0,0,1],
[-1,0,0,1,0,-1,0],
[1,1,0,-1,-1,0,0]]

def printcell(r,t,i,j,c):
    if c=="B":
        print(r"\mkFill{"+str(r)+"}{"+str(t)+"}{"+str(i)+"}{"+str(j)+"}{blue}")
    if c=="R":
        print(r"\mkFill{"+str(r)+"}{"+str(t)+"}{"+str(i)+"}{"+str(j)+"}{red}")
    if c=="Y":
        print(r"\mkFill{"+str(r)+"}{"+str(t)+"}{"+str(i)+"}{"+str(j)+"}{yellow}")
    if c=="G":
        print(r"\mkFill{"+str(r)+"}{"+str(t)+"}{"+str(i)+"}{"+str(j)+"}{gray}")

def modeltmp(model,inputs,rules):
    if len(inputs) != len(rules[0])-1:
        print(len(inputs))
        print("error")
        exit()
    for r in rules:
        expr = 0
        for i in range(0,len(r)-1):
            expr += r[i]*inputs[i]
        model.addConstr(expr + r[-1] >= 0)

def setcolor(model,color,r,i):
    if color ==0:
        model.addConstr(x_blue_state_S[r][i] == 0)
        model.addConstr(x_red_state_S[r][i] == 0)
    if color ==1:
        model.addConstr(x_blue_state_S[r][i] == 1)
        model.addConstr(x_red_state_S[r][i]  == 0)
    if color ==2:
        model.addConstr(x_blue_state_S[r][i] == 0)
        model.addConstr(x_red_state_S[r][i]  == 1)
    if color ==3:
        model.addConstr(x_blue_state_S[r][i] == 1)
        model.addConstr(x_red_state_S[r][i]  == 1)

def substates_shiftrow(substates,COL):
    ans = []
    for j in range(0,4):
        for i in range(0,COL):
            ans.append(substates[(COL*j+(COL+1)*i)%(4*COL)])
    return ans

def printstate(state):
    for i in range(0,4):
        print(state[0+i], state[4+i], state[8+i], state[12+i])

def chulistate(inputstate):
    ans = []
    for i in range(0,len(inputstate)):
        if inputstate[i] == 0:
            ans.append("W")
        elif inputstate[i] == 1:
            ans.append("B")
        elif inputstate[i] == 2:
            ans.append("R")
        elif inputstate[i] == 3:
            ans.append("G")
        elif inputstate[i] == 4:
            ans.append("Y")
        else:
            ans.append("error")
    return ans

def MC_con(model,input_col_blue,input_col_red,input_col_yellow,input_col_white,output_col_blue,output_col_red,output_col_yellow,consume_blue,consume_red): #using method from crypto2022 baozhenzhen
    exist_white = model.addVar(vtype=GRB.BINARY)
    all_blue_gray = model.addVar(vtype=GRB.BINARY)
    all_red_gray = model.addVar(vtype=GRB.BINARY)
    exist_yellow = model.addVar(vtype=GRB.BINARY)

    sum_input_white = 0
    for i in range(0,len(input_col_white)):
        sum_input_white += input_col_white[i]
    model.addConstr(4*exist_white - sum_input_white >= 0)
    model.addConstr(exist_white - sum_input_white <= 0)


    sum_input_blue = 0
    for i in range(0,len(input_col_blue)):
        sum_input_blue += input_col_blue[i]
    model.addConstr(sum_input_blue - 4*all_blue_gray >= 0)
    model.addConstr(sum_input_blue - all_blue_gray <= 3)

    sum_input_red = 0
    for i in range(0,len(input_col_red)):
        sum_input_red += input_col_red[i]
    model.addConstr(sum_input_red - 4*all_red_gray >= 0)
    model.addConstr(sum_input_red - all_red_gray <= 3)

    sum_input_yellow = 0
    for i in range(0,len(input_col_yellow)):
        sum_input_yellow += input_col_yellow[i]
    model.addConstr(4*exist_yellow - sum_input_yellow >= 0)
    model.addConstr(exist_yellow - sum_input_yellow <= 0)

    sum_output_blue = 0
    for i in range(0,len(output_col_blue)):
        sum_output_blue += output_col_blue[i]
    model.addConstr(sum_output_blue + 4*exist_white <= 4)
    model.addConstr(sum_output_blue + sum_input_blue - 8*all_blue_gray >=0)
    model.addConstr(sum_output_blue + sum_input_blue - 5*all_blue_gray <= 8-5)

    sum_output_red = 0
    for i in range(0,len(output_col_red)):
        sum_output_red += output_col_red[i]
    model.addConstr(sum_output_red + 4*exist_white <= 4)
    model.addConstr(sum_output_red + sum_input_red - 8*all_red_gray >=0)
    model.addConstr(sum_output_red + sum_input_red - 5*all_red_gray <= 8-5)

    sum_output_yellow = 0
    for i in range(0,len(output_col_yellow)):
        sum_output_yellow += output_col_yellow[i]
    model.addConstr(sum_output_yellow + 4*exist_white <= 4)

    model.addConstr(sum_output_red - 4*all_red_gray - consume_blue == 0)
    model.addConstr(sum_output_blue - 4*all_blue_gray - consume_red == 0)

def Match_con(model,input_col_white,output_col_white,match_ability):
    sum_input_white = 0
    for i in range(0,len(input_col_white)):
        sum_input_white += input_col_white[i]
    sum_output_white = 0
    for i in range(0,len(output_col_white)):
        sum_output_white += output_col_white[i]
    temp = model.addVar(vtype=GRB.INTEGER)
    model.addConstr(temp ==8 - sum_input_white - sum_output_white)
    model.addConstr(match_ability == gp.max_(temp,4))

def SR_get(inputstate):
    ans = []
    for i in range(0,16):
        ans.append(inputstate[(4*(i%4)+i)%16])
    return ans
def COL_get(inputstate,col):
    ans = []
    for i in range(0,4):
        ans.append(inputstate[4*col + i])
    return ans

if __name__ == "__main__":
    m = gp.Model("Areion256_mitm")
    m.Params.Threads = 2

    ROUNDS = 5
    ROW = 4
    COL = 4

    initial_round = 0
    match_round = 2
   
    initial_degree_forward = m.addVar(vtype=GRB.INTEGER, name="initial_degree_forward")
    initial_degree_backward = m.addVar(vtype=GRB.INTEGER, name="initial_degree_backward")
    x_blue   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="x_blue") #Blue Forward
    x_red    = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="x_red") #Red Backward
    x_yellow = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="x_yellow")
    x_gray   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="x_gray")
    x_white  = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="x_white")
    sx_blue   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sx_blue") #Blue Forward
    sx_red    = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sx_red") #Red Backward
    sx_yellow = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sx_yellow")
    sx_gray   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sx_gray")
    sx_white  = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sx_white")
    y_blue   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="y_blue") #Blue Forward
    y_red    = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="y_red") #Red Backward
    y_yellow = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="y_yellow")
    y_gray   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="y_gray")
    y_white  = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="y_white")
    sy_blue   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sy_blue") #Blue Forward
    sy_red    = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sy_red") #Red Backward
    sy_yellow = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sy_yellow")
    sy_gray   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sy_gray")
    sy_white  = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="sy_white")
    z_blue   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="z_blue") #Blue Forward
    z_red    = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="z_red") #Red Backward
    z_yellow = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="z_yellow")
    z_gray   = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="z_gray")
    z_white  = m.addVars(ROUNDS,ROW*COL,vtype=GRB.BINARY, name="z_white")
    x_mc_consume_blue = m.addVars(ROUNDS,COL,vtype=GRB.INTEGER, name="x_consume_blue") #Consume Blue MC
    x_mc_consume_red  = m.addVars(ROUNDS,COL,vtype=GRB.INTEGER, name="x_consume_red") #Consume Red MC
    y_mc_consume_blue = m.addVars(ROUNDS,COL,vtype=GRB.INTEGER, name="y_consume_blue") #Consume Blue MC
    y_mc_consume_red  = m.addVars(ROUNDS,COL,vtype=GRB.INTEGER, name="y_consume_red") #Consume Red MC
    xor_consume_blue = m.addVars(ROUNDS,ROW*COL,vtype=GRB.INTEGER, name="consume_blue") #Consume Blue XOR
    xor_consume_red  = m.addVars(ROUNDS,ROW*COL,vtype=GRB.INTEGER, name="consume_red") #Consume Red XOR
    xor_consume_blue2 = m.addVars(2,ROW*COL,vtype=GRB.INTEGER, name="consume_blue2") #Consume Blue XOR
    xor_consume_red2  = m.addVars(2,ROW*COL,vtype=GRB.INTEGER, name="consume_red2") #Consume Red XOR
    match_ability1 = m.addVars(COL,vtype=GRB.INTEGER, name="match_ability1")
    match_ability2 = m.addVars(COL,vtype=GRB.INTEGER, name="match_ability2")

    objective = m.addVar(vtype=GRB.INTEGER, name="objective")


    
    #Red Blue Yellow Gray Constraints
    for r in range(0,ROUNDS):
        for i in range(0,ROW*COL):
            m.addConstr(x_blue[r,i] - x_gray[r,i] >= 0)
            m.addConstr(x_red[r,i]  - x_gray[r,i] >= 0)
            m.addConstr(x_blue[r,i] + x_red[r,i] - 2*x_gray[r,i] <= 1)
            m.addConstr(y_blue[r,i] - y_gray[r,i] >= 0)
            m.addConstr(y_red[r,i]  - y_gray[r,i] >= 0)
            m.addConstr(y_blue[r,i] + y_red[r,i] - 2*y_gray[r,i] <= 1)
            m.addConstr(z_blue[r,i] - z_gray[r,i] >= 0)
            m.addConstr(z_red[r,i]  - z_gray[r,i] >= 0)
            m.addConstr(z_blue[r,i] + z_red[r,i] - 2*z_gray[r,i] <= 1)
            m.addConstr(1 - x_red[r,i]   - x_yellow[r,i] >= 0)
            m.addConstr(1 - x_blue[r,i]  - x_yellow[r,i] >= 0)
            m.addConstr(1 - y_red[r,i]   - y_yellow[r,i] >= 0)
            m.addConstr(1 - y_blue[r,i]  - y_yellow[r,i] >= 0)
            m.addConstr(1 - z_red[r,i]   - z_yellow[r,i] >= 0)
            m.addConstr(1 - z_blue[r,i]  - z_yellow[r,i] >= 0)
            m.addConstr(sx_blue[r,i] - sx_gray[r,i] >= 0)
            m.addConstr(sx_red[r,i]  - sx_gray[r,i] >= 0)
            m.addConstr(sx_blue[r,i] + sx_red[r,i] - 2*sx_gray[r,i] <= 1)
            m.addConstr(sy_blue[r,i] - sy_gray[r,i] >= 0)
            m.addConstr(sy_red[r,i]  - sy_gray[r,i] >= 0)
            m.addConstr(sy_blue[r,i] + sy_red[r,i] - 2*sy_gray[r,i] <= 1)
            m.addConstr(1 - sx_red[r,i]   - sx_yellow[r,i] >= 0)
            m.addConstr(1 - sx_blue[r,i]  - sx_yellow[r,i] >= 0)
            m.addConstr(1 - sy_red[r,i]   - sy_yellow[r,i] >= 0)
            m.addConstr(1 - sy_blue[r,i]  - sy_yellow[r,i] >= 0)
    #Red Blue Yellow White Constraints
    for r in range(0,ROUNDS):
        for i in range(0,ROW*COL):
            m.addConstr(x_white[r,i] + x_blue[r,i] + x_red[r,i] + x_yellow[r,i] >= 1)
            m.addConstr(x_white[r,i] <= 1 - x_red[r,i])
            m.addConstr(x_white[r,i] <= 1 - x_blue[r,i])
            m.addConstr(x_white[r,i] <= 1 - x_yellow[r,i])
            m.addConstr(y_white[r,i] + y_blue[r,i] + y_red[r,i] + y_yellow[r,i] >= 1)
            m.addConstr(y_white[r,i] <= 1 - y_red[r,i])
            m.addConstr(y_white[r,i] <= 1 - y_blue[r,i])
            m.addConstr(y_white[r,i] <= 1 - y_yellow[r,i])
            m.addConstr(z_white[r,i] + z_blue[r,i] + z_red[r,i] + z_yellow[r,i] >= 1)
            m.addConstr(z_white[r,i] <= 1 - z_red[r,i])
            m.addConstr(z_white[r,i] <= 1 - z_blue[r,i])
            m.addConstr(z_white[r,i] <= 1 - z_yellow[r,i])
            m.addConstr(sx_white[r,i] + sx_blue[r,i] + sx_red[r,i] + sx_yellow[r,i] >= 1)
            m.addConstr(sx_white[r,i] <= 1 - sx_red[r,i])
            m.addConstr(sx_white[r,i] <= 1 - sx_blue[r,i])
            m.addConstr(sx_white[r,i] <= 1 - sx_yellow[r,i])
            m.addConstr(sy_white[r,i] + sy_blue[r,i] + sy_red[r,i] + sy_yellow[r,i] >= 1)
            m.addConstr(sy_white[r,i] <= 1 - sy_red[r,i])
            m.addConstr(sy_white[r,i] <= 1 - sy_blue[r,i])
            m.addConstr(sy_white[r,i] <= 1 - sy_yellow[r,i])
    
    #Constraints for initial degree
    temp = 0
    for i in range(0,ROW*COL):
        temp += x_blue[initial_round,i] - x_gray[initial_round,i] + x_blue[(initial_round+1)%ROUNDS,i] - x_gray[(initial_round+1)%ROUNDS,i]
    m.addConstr(initial_degree_forward == temp)

    temp = 0
    for i in range(0,ROW*COL):
        temp += x_red[initial_round,i] - x_gray[initial_round,i] + x_red[(initial_round+1)%ROUNDS,i] - x_gray[(initial_round+1)%ROUNDS,i]
    m.addConstr(initial_degree_backward == temp)
    
    x_blue_state_S   = [[x_blue[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    x_red_state_S    = [[x_red[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    x_yellow_state_S = [[x_yellow[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    x_gray_state_S   = [[x_gray[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    x_white_state_S  = [[x_white[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sx_blue_state_S   = [[sx_blue[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sx_red_state_S    = [[sx_red[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sx_yellow_state_S = [[sx_yellow[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sx_gray_state_S   = [[sx_gray[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sx_white_state_S  = [[sx_white[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    
    y_blue_state_S   = [[y_blue[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    y_red_state_S    = [[y_red[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    y_yellow_state_S = [[y_yellow[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    y_gray_state_S   = [[y_gray[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    y_white_state_S  = [[y_white[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sy_blue_state_S   = [[sy_blue[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sy_red_state_S    = [[sy_red[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sy_yellow_state_S = [[sy_yellow[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sy_gray_state_S   = [[sy_gray[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    sy_white_state_S  = [[sy_white[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]


    z_blue_state_S   = [[z_blue[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    z_red_state_S    = [[z_red[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    z_yellow_state_S = [[z_yellow[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    z_gray_state_S   = [[z_gray[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]
    z_white_state_S  = [[z_white[r,i] for i in range(0,ROW*COL)]for r in range(0,ROUNDS)]

    for r in range(0,ROUNDS):
        # if (r!=(initial_round+match_round)%ROUNDS) and (r!=(initial_round+match_round+1)%ROUNDS):
        SR_state_blue   = SR_get(sx_blue_state_S[r])
        SR_state_red    = SR_get(sx_red_state_S[r])
        SR_state_yellow = SR_get(sx_yellow_state_S[r])
        SR_state_white  = SR_get(sx_white_state_S[r])
        for col in range(0,4):
            MC_con(m,COL_get(SR_state_blue,col), COL_get(SR_state_red,col), COL_get(SR_state_yellow,col), COL_get(SR_state_white,col),COL_get(y_blue_state_S[r],col), COL_get(y_red_state_S[r],col), COL_get(y_yellow_state_S[r],col), x_mc_consume_blue[r,col], x_mc_consume_red[r,col])
        for i in range(0,16):
            modeltmp(m,[y_blue_state_S[r][i],y_red_state_S[r][i],y_yellow_state_S[r][i],sy_blue_state_S[r][i],sy_red_state_S[r][i],sy_yellow_state_S[r][i]],SBOX_RULE)
        if (r!=(initial_round+match_round)%ROUNDS) and (r!=(initial_round+match_round+1)%ROUNDS):
            SR_state_blue  = SR_get(sy_blue_state_S[r])
            SR_state_red   = SR_get(sy_red_state_S[r])
            SR_state_yellow = SR_get(sy_yellow_state_S[r])
            SR_state_white = SR_get(sy_white_state_S[r])
            for col in range(0,4):
                MC_con(m,COL_get(SR_state_blue,col), COL_get(SR_state_red,col), COL_get(SR_state_yellow,col), COL_get(SR_state_white,col),COL_get(z_blue_state_S[r],col), COL_get(z_red_state_S[r],col), COL_get(z_yellow_state_S[r],col), y_mc_consume_blue[r,col], y_mc_consume_red[r,col])
        if (r==(initial_round+match_round)%ROUNDS):
            SR_state_blue  = SR_get(sx_blue_state_S[(r-2)%ROUNDS])
            SR_state_red   = SR_get(sx_red_state_S[(r-2)%ROUNDS])
            SR_state_yellow   = SR_get(sx_yellow_state_S[(r-2)%ROUNDS])
            SR_state_white = SR_get(sx_white_state_S[(r-2)%ROUNDS])
            for i in range(0,16):
                modeltmp(m,[SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],z_blue_state_S[(r-1)%ROUNDS][i],z_red_state_S[(r-1)%ROUNDS][i],z_yellow_state_S[(r-1)%ROUNDS][i],x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],xor_consume_blue[r,i],xor_consume_red[r,i]],XOR_RULE)
            for i in range(0,16):
                modeltmp(m,[x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i]],SBOX_RULE)
            SR_state_blue  = SR_get(sx_blue_state_S[(r-1)%ROUNDS])
            SR_state_red   = SR_get(sx_red_state_S[(r-1)%ROUNDS])
            SR_state_yellow   = SR_get(sx_yellow_state_S[(r-1)%ROUNDS])
            SR_state_white = SR_get(sx_white_state_S[(r-1)%ROUNDS])
            for i in range(0,16):
                modeltmp(m,[SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],x_blue_state_S[(r+1)%ROUNDS][i],x_red_state_S[(r+1)%ROUNDS][i],x_yellow_state_S[(r+1)%ROUNDS][i],z_blue_state_S[r][i],z_red_state_S[r][i],z_yellow_state_S[r][i],xor_consume_blue2[0,i],xor_consume_red2[0,i]],XOR_RULE)
        elif (r==(initial_round+match_round+1)%ROUNDS):
            SR_state_blue   = SR_get(sx_blue_state_S[r])
            SR_state_red    = SR_get(sx_red_state_S[r])
            SR_state_yellow = SR_get(sx_yellow_state_S[r])
            SR_state_white  = SR_get(sx_white_state_S[r])
            for i in range(0,16):
                modeltmp(m,[z_blue_state_S[(r+1)%ROUNDS][i],z_red_state_S[(r+1)%ROUNDS][i],z_yellow_state_S[(r+1)%ROUNDS][i],x_blue_state_S[(r+2)%ROUNDS][i],x_red_state_S[(r+2)%ROUNDS][i],x_yellow_state_S[(r+2)%ROUNDS][i],SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],xor_consume_blue[r,i],xor_consume_red[r,i]],XOR_RULE)
            for i in range(0,16):
                modeltmp(m,[sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i],x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i]],SBOX_RULE)
            SR_state_blue   = SR_get(sx_blue_state_S[(r-1)%ROUNDS])
            SR_state_red    = SR_get(sx_red_state_S[(r-1)%ROUNDS])
            SR_state_yellow = SR_get(sx_yellow_state_S[(r-1)%ROUNDS])
            SR_state_white  = SR_get(sx_white_state_S[(r-1)%ROUNDS])
            for i in range(0,16):
                modeltmp(m,[SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],x_blue_state_S[(r+1)%ROUNDS][i],x_red_state_S[(r+1)%ROUNDS][i],x_yellow_state_S[(r+1)%ROUNDS][i],z_blue_state_S[r][i],z_red_state_S[r][i],z_yellow_state_S[r][i],xor_consume_blue2[1,i],xor_consume_red2[1,i]],XOR_RULE)
        elif initial_round+match_round>ROUNDS:
            if (r>initial_round+1) or (r<(initial_round+match_round)%ROUNDS):
                SR_state_blue  = SR_get(sx_blue_state_S[(r-2)%ROUNDS])
                SR_state_red   = SR_get(sx_red_state_S[(r-2)%ROUNDS])
                SR_state_yellow   = SR_get(sx_yellow_state_S[(r-2)%ROUNDS])
                SR_state_white = SR_get(sx_white_state_S[(r-2)%ROUNDS])
                for i in range(0,16):
                    modeltmp(m,[SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],z_blue_state_S[(r-1)%ROUNDS][i],z_red_state_S[(r-1)%ROUNDS][i],z_yellow_state_S[(r-1)%ROUNDS][i],x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],xor_consume_blue[r,i],xor_consume_red[r,i]],XOR_RULE)
                for i in range(0,16):
                    modeltmp(m,[x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i]],SBOX_RULE)
            elif (r<initial_round) and (r>(initial_round+match_round+1)%ROUNDS):
                SR_state_blue   = SR_get(sx_blue_state_S[r])
                SR_state_red    = SR_get(sx_red_state_S[r])
                SR_state_yellow = SR_get(sx_yellow_state_S[r])
                SR_state_white  = SR_get(sx_white_state_S[r])
                for i in range(0,16):
                    modeltmp(m,[z_blue_state_S[(r+1)%ROUNDS][i],z_red_state_S[(r+1)%ROUNDS][i],z_yellow_state_S[(r+1)%ROUNDS][i],x_blue_state_S[(r+2)%ROUNDS][i],x_red_state_S[(r+2)%ROUNDS][i],x_yellow_state_S[(r+2)%ROUNDS][i],SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],xor_consume_blue[r,i],xor_consume_red[r,i]],XOR_RULE)
                for i in range(0,16):
                    modeltmp(m,[sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i],x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i]],SBOX_RULE)
            elif (r==initial_round) or (r==(initial_round+1)%ROUNDS):
                for i in range(0,16):
                    modeltmp(m,[x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i]],SBOX_RULE)

        elif initial_round+match_round<=ROUNDS:
            if (r>initial_round+1) and (r<(initial_round+match_round)):
                SR_state_blue  = SR_get(sx_blue_state_S[(r-2)%ROUNDS])
                SR_state_red   = SR_get(sx_red_state_S[(r-2)%ROUNDS])
                SR_state_yellow   = SR_get(sx_yellow_state_S[(r-2)%ROUNDS])
                SR_state_white = SR_get(sx_white_state_S[(r-2)%ROUNDS])
                for i in range(0,16):
                    modeltmp(m,[SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],z_blue_state_S[(r-1)%ROUNDS][i],z_red_state_S[(r-1)%ROUNDS][i],z_yellow_state_S[(r-1)%ROUNDS][i],x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],xor_consume_blue[r,i],xor_consume_red[r,i]],XOR_RULE)
                for i in range(0,16):
                    modeltmp(m,[x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i]],SBOX_RULE)
            elif (r<initial_round) or (r>(initial_round+match_round+1)):
                SR_state_blue   = SR_get(sx_blue_state_S[r])
                SR_state_red    = SR_get(sx_red_state_S[r])
                SR_state_yellow = SR_get(sx_yellow_state_S[r])
                SR_state_white  = SR_get(sx_white_state_S[r])
                for i in range(0,16):
                    modeltmp(m,[z_blue_state_S[(r+1)%ROUNDS][i],z_red_state_S[(r+1)%ROUNDS][i],z_yellow_state_S[(r+1)%ROUNDS][i],x_blue_state_S[(r+2)%ROUNDS][i],x_red_state_S[(r+2)%ROUNDS][i],x_yellow_state_S[(r+2)%ROUNDS][i],SR_state_blue[i],SR_state_red[i],SR_state_yellow[i],xor_consume_blue[r,i],xor_consume_red[r,i]],XOR_RULE)
                for i in range(0,16):
                    modeltmp(m,[sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i],x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i]],SBOX_RULE)
            elif (r==initial_round) or (r==(initial_round+1)%ROUNDS):
                for i in range(0,16):
                    modeltmp(m,[x_blue_state_S[r][i],x_red_state_S[r][i],x_yellow_state_S[r][i],sx_blue_state_S[r][i],sx_red_state_S[r][i],sx_yellow_state_S[r][i]],SBOX_RULE)
                
    match_L1 = SR_get(sy_white_state_S[(initial_round+match_round)%ROUNDS])
    for col in range(0,COL):
        Match_con(m,COL_get(match_L1,col), COL_get(z_white_state_S[(initial_round+match_round)%ROUNDS],col),match_ability1[col])
    match_L2 = SR_get(sy_white_state_S[(initial_round+match_round+1)%ROUNDS])
    for col in range(0,COL):
        Match_con(m,COL_get(match_L2,col), COL_get(z_white_state_S[(initial_round+match_round+1)%ROUNDS],col),match_ability2[col])
 
    objective1 = initial_degree_forward
    objective2 = initial_degree_backward

    for r in range(0,ROUNDS):
        for col in range(0,COL):
            objective1 = objective1 - x_mc_consume_blue[r,col] - y_mc_consume_blue[r,col]
            objective2 = objective2 - x_mc_consume_red[r,col] - y_mc_consume_red[r,col]
        for i in range(0,16):
            objective1 = objective1 - xor_consume_blue[r,i]
            objective2 = objective2 - xor_consume_red[r,i]
    for r in range(0,2):
        for i in range(0,16):
            objective1 = objective1 - xor_consume_blue2[r,i]
            objective2 = objective2 - xor_consume_red2[r,i]

    objective3 = 0
    for col in range(0,COL):
        objective3 = objective3 + match_ability1[col] + match_ability2[col]

    #temp = m.addVar(vtype=GRB.INTEGER)
    m.addConstr(objective <= objective1)
    m.addConstr(objective <= objective2)
    m.addConstr(objective <= objective3-32)
    m.setObjective(objective,GRB.MAXIMIZE)

    # colors = [[1,3,3,3,3,1,3,2,3,3,1,3,2,3,2,1],[3 for i in range(0,16)], [1,1,1,1,3,3,2,3,3,3,3,2,2,3,3,3],[1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0],[0,2,2,2,2,0,2,2,2,2,0,2,2,2,2,0]]

    # for r in range(0,5):
    #     for i in range(0,16):
    #         setcolor(m,colors[r][i],r,i)
   
    m.optimize()
    
    x_state = []
    y_state = []
    sx_state = []
    sy_state = []
    z_state = []
    for r in range(0,ROUNDS):
        x_state.append([])
        y_state.append([])
        sx_state.append([])
        sy_state.append([])
        z_state.append([])
        for i in range(0,ROW*COL):
            x_state[r].append(int(x_blue[r,i].x+x_red[r,i].x*2+x_yellow[r,i].x*4+0.1))
            y_state[r].append(int(y_blue[r,i].x+y_red[r,i].x*2+y_yellow[r,i].x*4+0.1))
            sx_state[r].append(int(sx_blue[r,i].x+sx_red[r,i].x*2+sx_yellow[r,i].x*4+0.1))
            sy_state[r].append(int(sy_blue[r,i].x+sy_red[r,i].x*2+sy_yellow[r,i].x*4+0.1))
            # if int(z_blue[r,i].x+z_red[r,i].x*2+0.1)==0 and int(z_white[r,i].x)!=1:
            #     print("error",r,i)
            z_state[r].append(int(z_blue[r,i].x+z_red[r,i].x*2+z_yellow[r,i].x*4+0.1))
    print([match_ability1[i].x for i in range(0,4)])
    print([match_ability2[i].x for i in range(0,4)])
    print(initial_degree_forward.x,initial_degree_backward.x)
    for r in range(0,ROUNDS):
        print("Round",r)
        x = chulistate(x_state[r])
        y = chulistate(y_state[r])
        sx = chulistate(sx_state[r])
        sy = chulistate(sy_state[r])
        z = chulistate(z_state[r])
        srx = SR_get(sx)
        sry = SR_get(sy)
        rx = SR_get(chulistate(sx_state[(r-1)%ROUNDS]))
        for i in range(0,4):
            for j in range(0,4):
                print(x[i+4*j],end = ' ')
            print("   ",end = '')
            for j in range(0,4):
                print(srx[i+4*j],end = ' ')
            print("   ",end = '')
            for j in range(0,4):
                print(y[i+4*j],end = ' ')
            print("   ",end = '')
            for j in range(0,4):
                print(sry[i+4*j],end = ' ')
            print("   ",end = '')
            for j in range(0,4):
                print(z[i+4*j],end = ' ')
            print("   ",end = '')
            for j in range(0,4):
                print(rx[i+4*j],end = ' ')
            print("")
        print("")
    for r in range(0,ROUNDS):
        #print("Round",r)
        x = chulistate(x_state[r])
        y = chulistate(y_state[r])
        sx = chulistate(sx_state[r])
        sy = chulistate(sy_state[r])
        z = chulistate(z_state[r])
        srx = SR_get(sx)
        sry = SR_get(sy)
        rx = SR_get(chulistate(sx_state[(r-1)%ROUNDS]))
        for i in range(0,4):
            for j in range(0,4):
                #print(x[i+4*j],end = ' ')
                printcell(r,0,i,j,x[i+4*j])
            #print("   ",end = '')
            for j in range(0,4):
                #print(srx[i+4*j],end = ' ')
                printcell(r,1,i,j,srx[i+4*j])
            #print("   ",end = '')
            for j in range(0,4):
                #print(y[i+4*j],end = ' ')
                printcell(r,2,i,j,y[i+4*j])
            #print("   ",end = '')
            for j in range(0,4):
                #print(sry[i+4*j],end = ' ')
                printcell(r,3,i,j,sry[i+4*j])
            #print("   ",end = '')
            for j in range(0,4):
                #print(z[i+4*j],end = ' ')
                printcell(r,4,i,j,z[i+4*j])
            #print("   ",end = '')
            for j in range(0,4):
                #print(rx[i+4*j],end = ' ')
                printcell(r,5,i,j,rx[i+4*j])
            print("")
        print("")
    # # for r in range(0,ROUNDS+1):
    # #     aa = chulistate(state[r])
    # #     bb = SR_get(aa)
    # #     if r == ROUNDS:
    # #         for i in range(0,16):
    # #             if aa[i]=="B":
    # #                 color = "blue"
    # #             elif aa[i]=="R":
    # #                 color = "red"
    # #             elif aa[i]=="G":
    # #                 color = "gray"
    # #             else:
    # #                 continue
    # #             print(r"\mkFill{"+str(r-1)+r"}{3}{"+str(i%4)+r"}{"+str(i//4)+r"}{"+color+r"}")
    # #         break

    # #     for i in range(0,16):
    # #         if aa[i]=="B":
    # #             color = "blue"
    # #         elif aa[i]=="R":
    # #             color = "red"
    # #         elif aa[i]=="G":
    # #             color = "gray"
    # #         else:
    # #             continue
    # #         print(r"\mkFill{"+str(r)+r"}{0}{"+str(i%4)+r"}{"+str(i//4)+r"}{"+color+r"}")
    # #         print(r"\mkFill{"+str(r)+r"}{1}{"+str(i%4)+r"}{"+str(i//4)+r"}{"+color+r"}")
    # #         if r>0:
    # #             print(r"\mkFill{"+str(r-1)+r"}{3}{"+str(i%4)+r"}{"+str(i//4)+r"}{"+color+r"}")
    # #     for i in range(0,16):
    # #         if bb[i]=="B":
    # #             color = "blue"
    # #         elif bb[i]=="R":
    # #             color = "red"
    # #         elif bb[i]=="G":
    # #             color = "gray"
    # #         else:
    # #             continue
    # #         print(r"\mkFill{"+str(r)+r"}{2}{"+str(i%4)+r"}{"+str(i//4)+r"}{"+color+r"}")
        
    # for r in range(0,ROUNDS):
    #     print("Round",r)
    #     printstate(chulistate(state[r]))

    # # r = 1
    # # col = 1
    # # SR_state_blue = SR_get(blue_state_S[r])
    # # SR_state_red = SR_get(red_state_S[r])
    # # SR_state_white = SR_get(white_state_S[r])

    # # inputblue = COL_get(SR_state_blue,col)
    # # inputred = COL_get(SR_state_red,col)
    # # outputblue = COL_get(blue_state_S[r+1],col)
    # # outputred = COL_get(red_state_S[r+1],col)

    # # for i in range(0,4):
    # #     print(int(inputblue[i].x+inputred[i].x*2+0.1),end = ' ')
    # # print('')
    # # for i in range(0,4):
    # #     print(int(outputblue[i].x + outputred[i].x*2 +0.1),end = ' ')
    # # print('')
    # # print(int(consume_blue[r,col].x+0.1),int(consume_red[r,col].x+0.1))



    # # m.addConstr(objective <= 31)
    # # m.setObjective(objective,GRB.MINIMIZE)

    # m.write('nnLesamntar.lp')
    # # m.optimize()
    # m.write('nnLesamnta256_rebounr.sol')

    # # filename = 'nnLesamnta256_rebound'+str(inround) +'_'+str(ROUNDS) + 'r.txt'

    # # with open(filename,mode="w") as f:
    # #     xstates = []
    # #     for r in range(0,ROUNDS+1):
    # #         xstate = []
    # #         for i in range(0,4):
    # #             xstatei = []
    # #             for j in range(0,4*COL):
    # #                 xstatei.append(int(x[r,i,j].x))
    # #             xstate.append(xstatei)
    # #         xstates.append(xstate)
    # #     for r in range(0,ROUNDS+1):
    # #         print("ROUND:"+str(r),file = f)
    # #         for i in range(0,COL):
    # #             for b in range(0,4):
    # #                 for j in range(0,4):
    # #                     print(xstates[r][b][COL*j+i],end = '',file = f)
    # #                 print("  ",end = '',file = f)
    # #             print("",file = f)
    # #     print("END",file = f)
    # # # xstates = []
    # # # for r in range(0,ROUNDS+1):
    # # #     xstate = []
    # # #     for i in range(0,4):
    # # #         xstatei = []
    # # #         for j in range(0,4*COL):
    # # #             xstatei.append(int(x[r,i,j].x))
    # # #         xstate.append(xstatei)
    # # #     xstates.append(xstate)
    # # # for r in range(0,ROUNDS+1):
    # # #     print("ROUND:"+str(r))
    # # #     for i in range(0,COL):
    # # #         for b in range(0,4):
    # # #             for j in range(0,4):
    # # #                 print(xstates[r][b][COL*j+i],end = '')
    # # #             print("  ",end = '')
    # # #         print("")
    # # # substates_xor_input = [x[0,3,i] for i in range(0,4*COL)]
    # # # substates_out = [x[1,0,i] for i in range(0,4*COL)]
    # # # substates_mc = [y[0,i] for i in range(0,4*COL)]
    # # # substates = [x[0,2,i] for i in range(0,4*COL)]
    # # # for i in substates_xor_input:
    # # #     print(i.x)
    # # # for i in substates_out:
    # # #     print(i.x)
    # # # for i in substates_mc:
    # # #     print(i.x)
    # # # for i in substates:
    # # #     print(i.x)
