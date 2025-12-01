// 定义 Promise 类型别名
type Promiser<T> = Promise<T>

interface ApiObject {
  getIdentifyingCode: (req?: any) => Promiser<any>;
}

