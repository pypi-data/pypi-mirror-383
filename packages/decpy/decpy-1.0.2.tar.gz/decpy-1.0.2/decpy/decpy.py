"""
Python Declarative Programming (DecPy) version 1.0.0

The BSD 3-Clause Copyright (c) 2025 Paul Dobryak (Pavel Vadimovich Dobryak)

A library for lazy evaluation and three types of declarative programming in Python:
1. An analogue of SQL (tuple calculus).
2. An analogue of QBE (domain calculus).
3. An analogue of Prolog (first-order predicate calculus, logic programming).
Recursive queries.

For the latest version and documentation, see
https://github.com/pauldobriak/DecPy

Author and programmer: Pavel Vadimovich Dobryak,
e-mail: goodsoul@mail.ru
https://vk.com/pauldobriak
tel, whatsapp: +79022726154
"""

from itertools import product
from functools import reduce

#Множественный конструктор
def multiconstr(cls):
    def wrapper(*n):
        if len(n)==0:
            return cls()
        elif len(n)==1 and type(n[0])==int:
            return (cls() for i in range(n[0]))
        else:
            return cls(*n)
    return wrapper

#ленивое выражение
class expr:
    def __init__(self,arg1,op,arg2):
        self.arg1=arg1
        self.op=op
        self.arg2=arg2
        self.recstart=False
    def __call__(self,*args):
        #вычисления с рекурсиями
        if self.recstart:
            n=0
            buf=self.recparam[0].value
            self.recparam[0].value=lazyset()
            while True:
                R=self.callmain(*args)
                if len(R)==n:
                    break
                n=len(R)
                self.recparam[0].value=lazyset(R)
            self.recparam[0].value=buf
            return lazyset(R)
        else:
            return self.callmain(*args)
    def __iter__(self):
        return self().__iter__()
    def __next__(self):
        return self().__next__()
    #вычисления или выполнение запросов без рекурсий
    def callmain(self,*args):
            if len(args)>0:
                sign = self.createsign()
                for i in range(len(sign)):
                    sign[i](args[i])
            arg1 = self.arg1
            #проверка на цепочку умножений
            manymult=False
            if type(arg1)==expr and arg1.op=="*" and self.op=="*":
                manymult=True
            elif type(arg1)==lazyindex and type(arg1.obj)==expr and arg1.obj.op=="*" and self.op=="*":
                manymult=True
            # получение выборок, вычислений; прерывание вызовов, если аргумент - класс.
            while callable(arg1):
                if hasattr(arg1,"__dict__") and ("qrcls" in arg1.__dict__) and (arg1.__dict__["qrcls"]==True):
                    break
                arg1=arg1()
            arg2 = self.arg2
            while callable(arg2):
                if hasattr(arg2,"__dict__") and ("qrcls" in arg2.__dict__) and (arg2.__dict__["qrcls"]==True):
                    break
                arg2=arg2()
            if self.op=="+":
                return arg1+arg2
            elif self.op=="*":
                if manymult and type(arg1) is multset and type(arg2) is multset:
                    return arg1.specialmult(arg2)
                if type(arg1)==set or type(arg2)==set:
                    return multset(arg1)*multset(arg2)
                return arg1*arg2
            elif self.op=="**":
                #заплатка - дополнительные проверки
                if type(arg1)==set or type(arg2)==set:
                    return multset(arg1)**multset(arg2)
                return arg1**arg2
            elif self.op=="<":
                return arg1<arg2
            elif self.op=="<=":
                return arg1<=arg2
            elif self.op=="==":
                return arg1==arg2
            elif self.op==">=":
                return arg1>=arg2
            elif self.op==">":
                return arg1>arg2
            elif self.op=="!=":
                return arg1!=arg2
            elif self.op=="&":
                return arg1 & arg2
            elif self.op=="|":
                return arg1 | arg2
            elif self.op=="|=":
                return arg2
            elif self.op=="/":
                return arg1 / arg2
            elif self.op=="//":
                return arg1 // arg2
            elif self.op=="%":
                return arg1 % arg2
            elif self.op=="-":
                return arg1 - arg2
            elif self.op=="^":
                return arg1 ^ arg2
            elif self.op=="neg":
                return -arg1
                          
    def __str__(self):
        return str(self())
    def __add__(self,other):
        return expr(self,"+",other)
    def __mul__(self,other):
        return expr(self,"*",other)
    def __pow__(self,other):
        return expr(self,"**",other)
    def __or__(self,other):
        return expr(self,"|",other)
    def __sub__(self,other):
        return expr(self,"-",other)
    def __xor__(self,other):
        return expr(self,"^",other)
    def __lt__(self,other):
        return expr(self,"<",other)
    def __le__(self,other):
        return expr(self,"<=",other)
    def __eq__(self,other):
        return expr(self,"==",other)
    def __ge__(self,other):
        return expr(self,">=",other)
    def __gt__(self,other):
        return expr(self,">",other)
    def __ne__(self,other):
        return expr(self,"!=",other)
    def __and__(self,other):
        return expr(self,"&",other)

    def __truediv__(self,other):
        return expr(self,"/",other)
    def __floordiv__(self,other):
        return expr(self,"//",other)
    def __neg__(self):
        return expr(self,"neg",None)
    def __mod__(self,other):
        return expr(self,"%",other)
    # определение новых понятий в стиле пролога
    def __ior__(self,other):
        L=reccheck(self,other)
        if len(L)>0:
            #проталкивание индекса внутрь выражения:
            if type(other)==lazyindex:
                A=var()[other.arg]
                other = other.obj
                R = indpropagation(A,other)
                other.recstart=True
                other.recparam=L
                return R
            else:
                other.recstart=True
                other.recparam=L
                return other
        return other
    # создание сигнатуры для превращения ленивого выражения в функцию
    def createsign(self,L=None):
        if L==None:
            L=[]
        if callable(self.arg1):
            self.arg1.createsign(L)
        if callable(self.arg2):
            self.arg2.createsign(L)
        return L
    def __getattr__(self,attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return lazyattr(self,attr)
    def __getitem__(self,ind):
        return lazyindex(self,ind)

    
#ленивая функция (в том числе - метод) для внутреннего использования    
def lazyfunc(f):           
    class wrapper(expr):
        def __init__(self,*args):
            self.args=args
        def __call__(self,*args):
            if len(args)>0:
                sign = self.createsign()
                for i in range(len(sign)):
                    sign[i](args[i])
            return f(*self.args)
        def createsign(self,L=None):
            if L==None:
                L=[]
            for arg in self.args:
                if callable(arg):
                    arg.createsign(L)
            return L
    def res(*args):
        return wrapper(*args)
    def __repr__(self):
        return str(self())
    res.lzfnc=True
    return res

#ленивая функция, например, для встраивания в формулу функций библиотеки math
def lazyfun(f):
    @lazyfunc
    def wrapper(*args):
        return f(*[a() for a in args])
    return wrapper

#абстрактный класс c ленивыми вычислительными методами
class calculus:
    def __len__(self):
        return len(self())
    @lazyfunc
    def len(self):
        return len(self())
    @lazyfunc
    def sum(self):
        return sum(self())
    @lazyfunc
    def min(self,arg=lambda x:x):
        return min(self(),key=arg)
    @lazyfunc
    def max(self,arg=lambda x:x):
        return max(self(),key=arg)
    @lazyfunc
    def avg(self):
        return sum(self())/len(self())
    @lazyfunc
    def sorted(self,arg=lambda x:x):
        return sorted(self(),key=arg)
    @lazyfunc
    def group(self):
        return self()
    @lazyfunc
    def distinct(self):
        return type(self())(set(self()))
    @lazyfunc
    def reduce(self,arg):
        return reduce(arg,self())
    def All(self,arg):
        if type(arg) in [int,float,str]:
            a=var()
            arg = (a==arg)
        @lazyfunc
        def f(self):
            return all(arg(el) for el in self)
        return f
    def Any(self,arg):
        if type(arg) in [int,float,str]:
            a=var()
            arg = (a==arg)
        @lazyfunc
        def f(self):
            return any(arg(el) for el in self)
        return f

calcfunclist=[calculus.len,calculus.max,calculus.min,calculus.sum]

#абстрактный класс-предок для ленивого индекса и атрибута
class lazyabc(expr,calculus):
    def __init__(self,obj,arg):
        self.obj = obj
        self.arg = arg
    def __call__(self,*args):
        obj = self.obj
        if callable(obj):
            if not(hasattr(obj,"__dict__") and ("qrcls" in obj.__dict__) and (obj.__dict__["qrcls"]==True)):
                obj = obj(*args)
            else:
                obj = obj.value
        else:
            obj = obj.value
        return obj
    def createsign(self,L=None):
        return self.obj.createsign(L)
    

    
#Ленивый атрибут    
class lazyattr(lazyabc):    
    def __call__(self,*args):
        obj = super().__call__(*args)
        if self.arg in obj.__dict__:
            return obj.__dict__[self.arg]
        #Потенциально опасно, но устраняет необходимость писать код типа F=flight.L
        elif self.arg == "L":
            return set(obj.__dict__.values())
        

#Ленивый индекс
class lazyindex(lazyabc):
    def __call__(self,*args):
        obj = super().__call__(*args)
        #while callable(obj):
        #    obj=obj()
        while callable(obj):
            if hasattr(obj,"__dict__") and ("qrcls" in obj.__dict__) and (obj.__dict__["qrcls"]==True):
                break
            obj=obj()
        # Одно условие - исчисление на кортежах
        if callable(self.arg):
            #return type(obj)(el for el in obj if self.arg(el))
            #return type(obj)(self.arg(el) for el in obj if self.arg(el))
            if type(self.arg) is expr and self.arg.op not in ["<","<=","==",">=",">","!=","&","|","^"]:
                return type(obj)(self.arg(el) for el in obj)
            elif type(self.arg)in [expr,var]:#вероятно, ошибка - вместо var - vartype
                return type(obj)(el for el in obj if self.arg(el))
            else:
                if type(self.arg) is expr and self.arg.op in ["<","<=","==",">=",">","!=","&","|","^"]:
                    return type(obj)(self.arg(el) for el in obj if self.arg(el))
                else:
                    return type(obj)(self.arg(el) for el in obj)
        
        # Несколько условий - исчисление на доменах или проекция
        elif type(self.arg)==tuple:
            sign = []
            func = []
            example=None
            for el in obj:
                example = el
                break #для множеств с переменной длинной кортежей может понадобиться перебор всего множества
            if example==None:
                return multset()
            if type(example) in simpletypes:
                lenexample=1
            else:
                lenexample=len(example)
            # Проекция и исчисление на кортежах
            if lenexample>len(self.arg): 
                A = set()
                for el in obj:
                    f = True
                    for i in range(len(self.arg)):
                        if type(self.arg[i]) is expr:
                            if not(self.arg[i](el)):
                                f=False
                                break
                    if f:
                        a=[]
                        for i in range(len(self.arg)):
                            if type(self.arg[i]) in [lazyindex,lazyattr,expr]:
                                xx=self.arg[i](el)
                                if type(xx)!=bool:
                                    a.append(xx)
                                else:
                                    a.append(el)
                        if len(a)==1:
                            A.add(a[0])
                        else:
                            A.add(tuple(a))
                return multset(A)
            # Исчисление на доменах
            else:
                #группировка
                g=False
                lg=0
                arggroup=[None]*min(len(self.arg),lenexample)
                for i in range(min(len(self.arg),lenexample)):
                    if type(self.arg[i])==vargrouptype:
                        g=True
                        lg=lg+1
                        arggroup[i]=var()
                if g:
                    grp = lazyset(obj)[*arggroup]
                    res = lazyset()
                    for el in grp:
                        k=0
                        arggroup1=[var() for a in range(len(arggroup))]
                        for i in range(len(arggroup)):
                            if type(arggroup[i])==vartype:
                                if lg>1:
                                    arggroup1[i]=el[k]
                                else:
                                    arggroup1[i]=el
                                k=k+1
                        grp1=lazyset(obj)[*arggroup1]
                        b=[]
                        for i in range(len(arggroup1)):
                            if type(arggroup1[i])==vartype:
                                b.append([])
                            else:
                                b.append(arggroup1[i])
                        for a in grp1:
                            for i in range(len(a)):
                                if type(arggroup[i])!=vartype:
                                    b[i].append(a[i])
                        for i in range(len(b)):
                            if type(b[i])==list:
                                b[i]=tuple(b[i])
                        b=tuple(b)
                        res.add(b)
                    obj=res
                # Формирование сигнатуры условий без учета None
                for i in range(min(len(self.arg),lenexample)):
                    if self.arg[i]!=None:
                        sign.append(i)
                # Формирование списка условий
                for i in range(len(self.arg)):
                    if self.arg[i]!=None:
                        if callable(self.arg[i]):
                            func.append(self.arg[i])
                        # Создание функций - условий по заданным образцам
                        else:
                            if i<lenexample:
                                v=var()
                                func.append(v==self.arg[i])
                if lenexample==1:
                    A = {(el,) for el in obj}
                else:
                    A = {tuple(el[i] for i in sign) for el in obj}
                B=multset()
                # Проверки выборок
                for el in A:
                    f=True
                    # Проверки основных условий
                    for i in range(min(len(func),len(sign))):
                        if type(func[i])==funcanytype or type(func[i])==funcalltype:
                            if not(func[i](el[i])()):
                                f=False
                                break
                        elif type(func[i]) not in [vartype,lazyindex,lazyattr] and type(func[i]) not in agrfunctypes and not(func[i](el[i])): 
                            f=False
                            break
                    # Одинаковым переменным в выборках соответствуют одинаковые значения:
                    if f:
                        argname=[]
                        for i in range(lenexample):
                            if self.arg[i]!=None:
                                argname.append(self.arg[i])
                        mask=[True]*len(argname)
                        for i in range(len(argname)):
                            for j in range(i+1,len(argname)):
                                if argname[i] is argname[j]:
                                    mask[j]=False
                                    if el[i]!=el[j]:
                                        f=False
                                        break
                            if not(f):
                                break
                    # проверки дополнительных условий
                    if f:
                        
                        for i in range(len(sign),len(func)):            
                            S=func[i].createsign()
                            for j in range(len(S)):
                                for k in range(len(sign)):
                                    if S[j] is self.arg[sign[k]]:
                                        S[j](el[k])
                            if not(func[i]()):
                                f=False
                                break
                    # проекция - если выбирается индекс или атрибут, подменить элемент его составляющей
                    if f:
                        el=list(el)
                        for i in range(len(sign)):
                            if type(self.arg[sign[i]]) in [lazyindex,lazyattr] or self.arg[sign[i]] in calcfunclist: # calcfunclist вероятно не работает
                                #el[i]=self.arg[sign[i]](el[i])
                                xx=self.arg[sign[i]](el[i])
                                if type(xx)!=bool:
                                    el[i]=xx
                        el=tuple(el)
                    # Удаление дублирующих атрибутов
                    if f:
                        ex = tuple(el[i] for i in range(len(el)) if mask[i])
                    # добавление конструируемых атрибутов
                    if f:
                        ex = list(ex)
                        for i in range(lenexample,len(self.arg)):
                            if type(self.arg[i]) not in [expr,lazyindex,lazyattr,vartype] and self.arg[i] not in calcfunclist: # calcfunclist вероятно не работает
                                ex.append(self.arg[i])
                            elif type(self.arg[i])==vartype:
                                for j in range(len(sign)):
                                    if self.arg[i] is self.arg[sign[j]]:
                                        ex.append(el[j])
                            elif type(self.arg[i])==expr and self.arg[i].op not in ["<","<=","==",">=",">","!="] or type(self.arg[i]) in [lazyindex,lazyattr] or self.arg[i] in calcfunclist:
                                S=self.arg[i].createsign()
                                for j in range(len(S)):
                                    for k in range(len(sign)):
                                        if S[j] is self.arg[sign[k]]:
                                            S[j](el[k])
                                aa = self.arg[i]() #последнее условие с calculus очевидно не работает, поэтому проверка:
                                if type(aa) is not bool:
                                    ex.append(aa)
                        ex=tuple(ex)
                    # помещение кортежа в результат:
                    if f:
                        if len(ex)==1:
                            ex=ex[0]
                        B.add(ex)
                    
                return multset(B)
        # Числовой индекс или срез
        else:
            return obj.__getitem__(self.arg)
    
    #общий индекс из индексов аргументов при декартовом произведении
    def __pow__(self,other):
        if type(other)==lazyindex:
            return (self.obj ** other.obj)[self.arg + other.arg]
        else:
            return super().__pow__(other)
    def __ior__(self,other):
        L=reccheck(self.obj,other)
        if len(L)>0:
            other.recstart=True
            other.recparam=L
        R = indpropagation(self,other)
        return R

    

#проверка на наличие рекурсии
def reccheck(A,B,L=None):
    if L==None:
        L=[]
    if type(B)==expr:
        L = reccheck(A,B.__dict__["arg1"],L)
        L = reccheck(A,B.__dict__["arg2"],L)
    elif type(B)==lazyindex or type(B)==lazyattr:
        L = reccheck(A,B.__dict__["obj"],L)
    elif type(B)==vartype:
        if A is B:
            L.append(B)
    return L

#перестановка местами элементов кортежа
@lazyfunc
def subst(R,P):
    return ({tuple(el[i] for i in P) for el in R()})

#проталкивание левого индекса внутрь правого выражения
def indpropagation(self,other):
        if type(other)==lazyindex and (type(other.arg) is tuple) and (type(self.arg) is tuple):
            ind=[]
            for i in range(len(other.arg)):
                f=True
                for j in range(i):
                    if other.arg[i] is other.arg[j]:
                        f=False
                        break
                if f:
                    ind.append(other.arg[i])
            for i in range(len(ind)):
                f=True
                for j in range(len(self.arg)):    
                    if ind[i] is self.arg[j]:
                        f=False
                        break
                if f:
                    ind[i]=None
            R=other[*ind]
            # формирование подстановки
            ind1 = []
            for i in range(len(ind)):
                if ind[i]!=None:
                    ind1.append(ind[i])
            P=[]
            for i in range(len(self.arg)):
                for j in range(len(ind1)):
                    if self.arg[i] is ind1[j]:
                        P.append(j)
                        break
            #return R
            return subst(R,P)
        elif type(other)==expr and other.op=="|":
            other.arg1=indpropagation(self,other.arg1)
            other.arg2=indpropagation(self,other.arg2)
            return other
        elif type(other)==vartype:
            return other[self.arg]
        else:
            return other[self.arg]  
        
#Ленивая переменная    
@multiconstr
class var(expr,calculus):
    def __init__(self,value=None):
        self.value=value
    def __call__(self,*args):
        if len(args)==0:
            return self.value
        else:
            self.value=args[0]
            return self.value
    #добавление переменной в сигнатуру функции из ленивого выражения
    def createsign(self,L=None):
        if L==None:
            L=[]
        f = True
        for el in L:
            if self is el:
                f = False
        if f:
            L.append(self)
        return L
    def add(self,value):
        self.value.add(value)
    def append(self,value):
        self.value.append(value)    
    def __setitem__(self,ind,value):
        self(value)


#используемые для сравнения типы данных  
funcanytype = type(calculus.Any(var(),var()==5))
funcalltype = type(calculus.All(var(),var()==5))
vartype = type(var())
vargrouptype = type(var().group())
simpletypes = [int,float,str]
agrfunctypes = [type(var().sum()),type(var().len()),type(var().min()),type(var().max())]

#множество с операциями декартова произведения      
class multset(set):
    def __mul__(self,other):
        R=set()
        # попытка присоединения кортежей справа
        for el in self:
            exL=el
            if type(exL)==tuple:
                exa=exL[0]
                for el in other:
                    exb=el
                    break
                if type(exa)==type(exb):
                    return self.specialmult(other)
                else:
                    break
        # попытка присоединения кортежей слева
        for el in other:
            exL=el
            if type(exL)==tuple:
                exb=exL[0]
                for el in self:
                    exa=el
                    break
                if type(exa)==type(exb):
                    return self.specialmultleft(other)
                else:
                    break
        # декартово произведение
        for a in self:
            for b in other:
                R.add((a,b))
        return multset(R)
    def specialmult(self,other):
        R=set()
        for a in self:
            for b in other:
                R.add((a+(b,)))
        return multset(R)
    def specialmultleft(self,other):
        R=set()
        for a in self:
            for b in other:
                R.add(((a,)+b))
        return multset(R)

    def __pow__(self,other):
        R=set()
        for a in self:
            for b in other:
                if type(a) in simpletypes:
                    a1=(a,)
                elif type(a) in [tuple,list]:
                    a1=a
                else:
                    a1=tuple(el for el in a)
                    #a1=tuple(a.__dict__.values())
                if type(b) in simpletypes:
                    b1=(b,)
                elif type(b) in [tuple,list]:
                    b1=b
                else:
                    b1=tuple(el for el in b)
                    #b1=tuple(b.__dict__.values())
                R.add(a1+b1)
        return multset(R)
    def __str__(self):
        f=True
        for el in self:
            if not(type(el)==tuple and len(el)==1):
                f=False
                break
        if f:
            return str({el[0] for el in self}) #вывод кортежа из одного элемента
        else:
            return str({el for el in self})

#создание ленивого множества с умножением (упаковка множества с умножением в ленивую переменную)
def lazyset(L=None):
    if L==None:
        L=set()
    M=multset(L)
    v=var()
    v(M)
    return v

#декоратор, добавляющий к классу экстент (экземпляры автоматически помещаются в ленивое множество)
def queryclass(cls):
    class metaset(type):
        def __init__(self,*args):
            self.L=lazyset()
            self.qrcls=True
        def __repr__(self):
            return self.L.__repr__
        def __getitem__(self,i):
            return self.L[i]
        def __str__(self):
            return self.L.__str__()
        def __or__(self,other):
            if type(other)==vartype:
                return self.L | other()
            else:
                return self.L | other.L
        def __and__(self,other):
            return self.L & other.L
        def __mul__(self,other):
            return self.L * other.L
        def __sub__(self,other):
            return self.L - other.L
        def __xor__(self,other):
            return self.L ^ other.L
        def __pow__(self,other):
            if type(other)==expr:
                return self.L ** other
            else:
                return self.L ** other.L
        def __iter__(self):
            return self.L().__iter__()
        def __next__(self):
            return self.L().__next__()
    class newclass(cls,metaclass=metaset):
        def __init__(self,*args):
            super().__init__(*args)
            self.__class__.L.add(self)
            self.__class__.L.L.name=cls.__name__

        def __getattr__(self,attr):
            if attr in self.__dict__:
                return self.__dict__[attr]
            elif attr=="L":
                return tuple(self.__dict__.values())

        def __getitem__(self,ind):
            return list(self.__dict__.values())[ind]
        def __len__(self):
            return len(list(self.__dict__.values()))
    return newclass


#превращение функции в предикат
class queryfun:
    def __init__(self,f):
        self.f=f
        self.L=lazyset()
    def __call__(self,*args):
        r=self.f(*args)
        self.L.add((*args,r))
        return r
    def __str__(self):
        return str(self.L)
    def __getitem__(self,ind):
        F=True
        for i in range(len(ind)-1):
            if type(ind[i]) in [expr,lazyindex,lazyset,vartype]:
                F=False
                break
        if F:
            r=(self(*ind[:-1]))
            if ind[-1] not in [expr,lazyindex,lazyset,vartype]:
                return r==ind[-1]
            else:
                return lazyset({*(list(ind)[:-1]),r})
        else:
            return self.L.__getitem__(ind)
    def init(self,*args):
        for arg in product(*args):
            self(*arg)

# строка таблицы - предиката
def tablerow(header,lst):
    class newclass:
        def __init__(self,header,lst):
            self.header=header
            self.L=lst
            self.qrcls=True
            # потенциально опасно, если будут изменяться значения атрибутов
            for i in range(len(header)):
                self.__dict__[header[i]]=self.L[i]
        def __getitem__(self,ind):
            return self.L[ind]
        def __getattr__(self,attr):
            if attr in self.__dict__:
                return self.__dict__[attr]
            elif attr in self.header:
                i=self.header.index(attr)
                return self.L[i]
        def __str__(self):
            return str(self.L)
        def __repr__(self):
            return str(self.L)
        def __len__(self):
            return len(list(self.L))
    res = newclass(header,lst)
    return res

# таблица - предикат
@multiconstr
class table:
    def __init__(self,*args):
        self.L=lazyset()
        self.header = (args)
        self.allowfact = True
        self.terms=[]
        self.recstart=False
    def __call__(self,*args):
        if self.allowfact:
            if len(self.header)==0:
                if len(args)==1:
                    self.L.add(args[0])
                else:
                    self.L.add(args)
                return args
            else:
                el = tablerow(self.header,args)
                self.L.add(el)
                return el
        else:
            n=len(self.L)
            while True:
                for el in self.realobj()():
                    self.L.add(el)
                if len(self.L)>n:
                    n=len(self.L)
                else:
                    break
            return self.L
    #подмена исходного множества на все добавленные и вычисленные
    def realobj(self):
        if self.allowfact:
            return self.L
        else:
            res = self.L
            for t in self.terms:
                res = res | t
            return res
    def __str__(self):
        if self.allowfact:
            return str(self.L)
        else:
            return str(self())
    def __getitem__(self,ind):
        return self.realobj()[ind]
    def __mul__(self,other):
        return self.realobj() * other.L
    def __pow__(self,other):
        return self.realobj() ** other.L
    def __or__(self,other):
        if type(other)!=table:
            return self.realobj() | other
        else:
            return self.realobj() | other.realobj()
    def __sub__(self,other):
        return self.realobj() - other
    def __xor__(self,other):
        return self.realobj() ^ other
    def __setitem__(self,ind,value):
        self.allowfact = False
        self.terms.append(value[ind])
        return self
    def __ior__(self,other):
        self.allowfact = False
        self.terms.append(other)
        return self
    def __iter__(self):
        return self.realobj()().__iter__()
    def __next__(self):
        return self.realobj()().__next__()

@lazyfunc
def packelements(L):
    return lazyset({(el,) for el in L})

@lazyfunc
def lazyrange(*args):
    fin=0
    if len(args)==1:
        start=0
        fin = args[0]
        cond=lambda x : x<fin
        func=lambda x : x+1
    elif len(args)==2:
        start = args[0]
        fin = args[1]
        if start < fin:
            cond=lambda x : x<fin
            func=lambda x : x+1
        else:
            cond=lambda x : x>fin
            func=lambda x : x-1
    elif len(args)==3 and type(args[2]) in [int,float]:
        start = args[0]
        fin = args[1]
        if start < fin:
            cond=lambda x : x<fin
        else:
            cond=lambda x : x>fin
        func=lambda x : x+args[2]
    elif len(args)==3:
        start = args[0]
        fin = args[1]
        if start < fin:
            cond=lambda x : x<fin
        else:
            cond=lambda x : x>fin
        func=args[2]
    else:
        #Для последовательностей типа чисел Фибоначчи
        L = list(args[:-2])
        fin = args[-2]
        if L[0] < fin:
            cond=lambda x : x<fin
        else:
            cond=lambda x : x>fin
        func=args[-1]
        n=len(args)-2
        while cond(L[-1]):
            r=func(*L[-n:])
            if cond(r):
                L.append(r)
            else:
                break
        return L
    #для обычных прогрессий
    n=start
    L=[]
    while cond(n):
        L.append(n)
        #yield n
        n=func(n)
    return L

