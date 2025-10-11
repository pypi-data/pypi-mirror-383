class Array:
    def __init__(self, data):
        if isinstance(data, Array):
            self.data = self._deepcopy(data.data)
        elif isinstance(data, (int, float, bool)):
            self.data = [data]
        elif isinstance(data, (list, tuple)):
            self.data = self._deepcopy(list(data))
        else:
            raise TypeError("Unsupported type")
        self.shape = self._infer_shape(self.data)
        self.nested_data = self.data

    def __repr__(self):
        return f"Array(shape={self.shape}, data={self.nested_data})"

    # ---------------- Helpers ----------------
    def _deepcopy(self, obj):
        if isinstance(obj,list):
            return [self._deepcopy(x) for x in obj]
        return obj

    def _infer_shape(self, data):
        if isinstance(data,list):
            if len(data)==0: return (0,)
            sub = self._infer_shape(data[0])
            return (len(data),) + sub
        return ()

    def flatten(self):
        return Array(self._flatten_recursive(self.nested_data))

    def _flatten_recursive(self, nested):
        result = []
        for item in nested:
            if isinstance(item,list):
                result.extend(self._flatten_recursive(item))
            else:
                result.append(item)
        return result

    def reshape(self, shape):
        shape = tuple(shape)
        flat = self.flatten().data
        unknown_idx = -1
        total_size = 1
        for i,dim in enumerate(shape):
            if dim==-1:
                unknown_idx = i
            else:
                total_size *= dim
        if unknown_idx!=-1:
            inferred = len(flat)//total_size
            shape = shape[:unknown_idx]+(inferred,)+shape[unknown_idx+1:]
        if len(flat) != (1 if total_size==1 else total_size*shape.count(-1) or len(flat)):
            raise ValueError("Cannot reshape")
        self.shape = shape
        self.nested_data = self._reshape_recursive(flat, shape)

    def _reshape_recursive(self, data, shape):
        if len(shape)==1: return data
        size = shape[0]
        chunk = len(data)//size
        return [self._reshape_recursive(data[i*chunk:(i+1)*chunk], shape[1:]) for i in range(size)]

    # ---------------- Arithmetic & Broadcasting ----------------
    def _broadcast_shapes(self, shape1, shape2):
        result = []
        max_len = max(len(shape1), len(shape2))
        shape1 = (1,)*(max_len-len(shape1))+shape1
        shape2 = (1,)*(max_len-len(shape2))+shape2
        for s1,s2 in zip(shape1,shape2):
            if s1==s2 or s1==1 or s2==1:
                result.append(max(s1,s2))
            else:
                raise ValueError(f"Incompatible shapes {shape1} and {shape2}")
        return tuple(result)

    def _broadcast_to(self, target_shape, data=None, shape=None):
        if data is None: data=self.nested_data
        if shape is None: shape=self.shape
        if len(shape)<len(target_shape):
            data=[data]
            shape=(1,)+shape
        if shape==target_shape: return data
        if len(shape)!=len(target_shape): raise ValueError("Cannot broadcast")
        result=[]
        for i in range(target_shape[0]):
            idx=i%shape[0]
            if len(shape)==1:
                result.append(data[idx])
            else:
                result.append(self._broadcast_to(target_shape[1:], data[idx], shape[1:]))
        return result

    def _apply_op(self, other, op, return_bool=False):
        if isinstance(other, Array):
            target_shape=self._broadcast_shapes(self.shape, other.shape)
            a=self._broadcast_to(target_shape)
            b=other._broadcast_to(target_shape)
            def apply(x,y):
                if isinstance(x,list):
                    return [apply(xx,yy) for xx,yy in zip(x,y)]
                return op(x,y)
            data=apply(a,b)
        else:
            def apply_scalar(x):
                if isinstance(x,list):
                    return [apply_scalar(xx) for xx in x]
                return op(x,other)
            data=apply_scalar(self.nested_data)
            target_shape=self.shape
        result=Array(self._flatten_recursive(data))
        result.reshape(target_shape)
        if return_bool: result=result.astype(bool)
        return result

    # ---------------- Arithmetic ----------------
    def __add__(self, other): return self._apply_op(other, lambda a,b:a+b)
    def __sub__(self, other): return self._apply_op(other, lambda a,b:a-b)
    def __mul__(self, other): return self._apply_op(other, lambda a,b:a*b)
    def __truediv__(self, other): return self._apply_op(other, lambda a,b:a/b)
    def __pow__(self, other): return self._apply_op(other, lambda a,b:a**b)

    # ---------------- Comparison ----------------
    def __gt__(self, other): return self._apply_op(other, lambda a,b:a>b, return_bool=True)
    def __lt__(self, other): return self._apply_op(other, lambda a,b:a<b, return_bool=True)
    def __ge__(self, other): return self._apply_op(other, lambda a,b:a>=b, return_bool=True)
    def __le__(self, other): return self._apply_op(other, lambda a,b:a<=b, return_bool=True)
    def __eq__(self, other): return self._apply_op(other, lambda a,b:a==b, return_bool=True)
    def __ne__(self, other): return self._apply_op(other, lambda a,b:a!=b, return_bool=True)

    # ---------------- Logical ----------------
    def __and__(self, other): return self._apply_op(other, lambda a,b:a and b, return_bool=True)
    def __or__(self, other): return self._apply_op(other, lambda a,b:a or b, return_bool=True)
    def __invert__(self): return self._apply_op(True, lambda a,b: not a, return_bool=True)
    def astype(self, typ):
        def convert(x):
            if isinstance(x,list):
                return [convert(xx) for xx in x]
            return typ(x)
        r=Array(convert(self.nested_data))
        r.shape=self.shape
        return r

    # ---------------- Aggregate functions ----------------
    def sum(self, axis=None):
        return self._aggregate(axis, sum)
    def mean(self, axis=None):
        from statistics import mean
        return self._aggregate(axis, mean)
    def max(self, axis=None):
        return self._aggregate(axis, max)
    def min(self, axis=None):
        return self._aggregate(axis, min)

    def _aggregate(self, axis, func):
        flat=self.flatten().data
        if axis is None: return func(flat)
        if len(self.shape)!=2: raise NotImplementedError("Axis only for 2D")
        rows,cols=self.shape
        res=[]
        if axis==0:
            for c in range(cols): res.append(func([self.nested_data[r][c] for r in range(rows)]))
        else:
            for r in range(rows): res.append(func(self.nested_data[r]))
        return Array(res)

    # ---------------- Dot / Matrix Multiplication ----------------
    def dot(self, other):
        if len(self.shape)!=2 or len(other.shape)!=2: raise ValueError("Dot requires 2D")
        if self.shape[1]!=other.shape[0]: raise ValueError("Shapes incompatible")
        rows,cols=self.shape[0],other.shape[1]
        data=[]
        for r in range(rows):
            for c in range(cols):
                data.append(sum(self.nested_data[r][k]*other.nested_data[k][c] for k in range(self.shape[1])))
        res=Array(data)
        res.reshape((rows,cols))
        return res
