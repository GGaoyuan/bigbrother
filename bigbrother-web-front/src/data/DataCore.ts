class DataCenter {
  private static instance: DataCenter | null = null;

  // 私有构造函数，防止外部直接实例化
  private constructor() {
    // 初始化逻辑
  }

  // 获取单例实例
  public static getInstance(): DataCenter {
    if (!DataCenter.instance) {
      DataCenter.instance = new DataCenter();
    }
    return DataCenter.instance;
  }

  // 可以在这里添加你的数据和方法
  // 例如：
  // private data: any = {};
  // 
  // public setData(key: string, value: any) {
  //   this.data[key] = value;
  // }
  // 
  // public getData(key: string) {
  //   return this.data[key];
  // }
}

// 导出单例实例，这样在任何地方都可以直接使用
export const dataCenter = DataCenter.getInstance();

// 也可以导出类，如果需要的话
export default DataCenter;