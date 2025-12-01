import axios from "axios";

export async function post<T>(url: string, req: T, options?: any) {
  if (options && options.headers && sessionStorage.getItem("acNo"))
    options.headers.Acno = sessionStorage.getItem("acNo");


  // const _req: any = { activityCode: getQueryString("activity"),  ...req };
  // const _req: any = { ...req };
  // const data: any = axios
  //     .post(apiUrl + url, _req, getConfig(options))
  //     .then((res) => {
  //       if (res.status == 200) {
  //         return res.data;
  //       } else if (res.status === 401) {
  //         (that as any).$$store.commit("showLogin", true);
  //       } else {
  //         return { retCode: "999000", retDesc: "网络异常，请稍后重试" };
  //       }
  //     })
  //     .catch((e) => {
  //       return { retCode: "999000", retDesc: "网络异常，请稍后重试" };
  //     })
  //     .finally(() => {
  //       nprogress.done();
  //     });
  // return data;
}
