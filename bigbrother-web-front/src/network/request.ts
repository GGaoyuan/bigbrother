import axios from "axios";

const that = this;

function getConfig(options: any = { headers: {}, other: {} }) {
  const headerOpt = options.headers || {};
  const ohterOpt = options.other || {};
  return {
    timeout: 60000,
    headers: {
        Authorization:'',
        common: {
            "x-auth-token": "",
        },
        post: {
            "x-auth-token": "",
        },
        "Content-Type": "application/json",
        ...headerOpt,
    },
    ...ohterOpt,
    withCredentials: true,
  };
}

export async function post<T>(url: string, req: T, options?: any) {
  // if (options && options.headers && sessionStorage.getItem("acNo"))
  //   options.headers.Acno = sessionStorage.getItem("acNo");

  const apiUrl = "http://127.0.0.1:5000"
  // const _req: any = { activityCode: getQueryString("activity"),  ...req };
  const _req: any = { ...req };
  return axios.post(apiUrl + url, _req, getConfig(options))
      .then((res) => {
        console.log("response = ", res.data);
        if (res.status == 200) {
          return res.data;
        } else if (res.status === 401) {
          (that as any).$$store.commit("showLogin", true);
        } else {
          return {retCode: "999000", retDesc: "网络异常，请稍后重试"};
        }
      })
      .catch((e) => {
        console.log("response error = ", e );
        return {retCode: "999000", retDesc: "网络异常，请稍后重试"};
      })
      .finally(() => {
        console.log(22222222);
      });
}
