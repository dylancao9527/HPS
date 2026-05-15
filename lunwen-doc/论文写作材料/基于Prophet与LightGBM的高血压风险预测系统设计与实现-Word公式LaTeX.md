# Word 公式 LaTeX 粘贴清单

使用方法：在 Word 中按 `Alt+=` 插入公式，粘贴“Word 公式输入”这一行，按空格或回车转换为专业公式。`#(编号)` 是 Word 公式编号的线性输入写法，正常情况下会把编号靠右显示。

如果 Word 的 LaTeX 模式不识别 `#(编号)`，可改用无边框表格：插入 1 行 2 列表格，左侧单元格居中放公式，右侧单元格右对齐输入编号，然后取消边框。

## 公式（1）

LaTeX 公式本体：

```latex
\mathbf{Y}_{1:T}=\{y_1,y_2,\ldots,y_T\},\quad y_t=(SBP_t,DBP_t,HR_t)
```

Word 公式输入：

```latex
\mathbf{Y}_{1:T}=\{y_1,y_2,\ldots,y_T\},\quad y_t=(SBP_t,DBP_t,HR_t)#(1)
```

## 公式（2）

LaTeX 公式本体：

```latex
\widehat{y}_{T+h}=f(y_T,y_{T-1},\ldots,y_{T-p+1}),\quad h=1,2,\ldots,H
```

Word 公式输入：

```latex
\widehat{y}_{T+h}=f(y_T,y_{T-1},\ldots,y_{T-p+1}),\quad h=1,2,\ldots,H#(2)
```

## 公式（3）

LaTeX 公式本体：

```latex
y_t=\tau_t+s_t+r_t
```

Word 公式输入：

```latex
y_t=\tau_t+s_t+r_t#(3)
```

## 公式（4）

LaTeX 公式本体：

```latex
y(t)=g(t)+s(t)+h(t)+\epsilon_t
```

Word 公式输入：

```latex
y(t)=g(t)+s(t)+h(t)+\epsilon_t#(4)
```

## 公式（5）

LaTeX 公式本体：

```latex
g(t)=(k+a(t)^{T}\delta)t+(m+a(t)^{T}\gamma)
```

Word 公式输入：

```latex
g(t)=(k+a(t)^{T}\delta)t+(m+a(t)^{T}\gamma)#(5)
```

## 公式（6）

LaTeX 公式本体：

```latex
F_M(x)=\sum_{m=1}^{M} f_m(x)
```

Word 公式输入：

```latex
F_M(x)=\sum_{m=1}^{M} f_m(x)#(6)
```

## 公式（7）

LaTeX 公式本体：

```latex
\mathcal{L}^{(m)}=\sum_{i=1}^{N}l(y_i,\hat{y}^{(m-1)}_i+f_m(x_i))+\Omega(f_m)
```

Word 公式输入：

```latex
\mathcal{L}^{(m)}=\sum_{i=1}^{N}l(y_i,\hat{y}^{(m-1)}_i+f_m(x_i))+\Omega(f_m)#(7)
```

## 公式（8）

LaTeX 公式本体：

```latex
w_j^{*}=-\frac{G_j}{H_j+\lambda}
```

Word 公式输入：

```latex
w_j^{*}=-\frac{G_j}{H_j+\lambda}#(8)
```

## 公式（9）

LaTeX 公式本体：

```latex
p=P(y=1\mid x)=\frac{1}{1+e^{-F_M(x)}}
```

Word 公式输入：

```latex
p=P(y=1\mid x)=\frac{1}{1+e^{-F_M(x)}}#(9)
```

## 公式（10）

LaTeX 公式本体：

```latex
\overline{SBP}_d=\frac{1}{n_d}\sum_{i=1}^{n_d}SBP_{d,i}
```

Word 公式输入：

```latex
\overline{SBP}_d=\frac{1}{n_d}\sum_{i=1}^{n_d}SBP_{d,i}#(10)
```

## 公式（11）

LaTeX 公式本体：

```latex
\overline{DBP}_d=\frac{1}{n_d}\sum_{i=1}^{n_d}DBP_{d,i}
```

Word 公式输入：

```latex
\overline{DBP}_d=\frac{1}{n_d}\sum_{i=1}^{n_d}DBP_{d,i}#(11)
```

## 公式（12）

LaTeX 公式本体：

```latex
SBP_{future}=\frac{1}{7}\sum_{k=1}^{7}\widehat{SBP}_{t+k}
```

Word 公式输入：

```latex
SBP_{future}=\frac{1}{7}\sum_{k=1}^{7}\widehat{SBP}_{t+k}#(12)
```

## 公式（13）

LaTeX 公式本体：

```latex
DBP_{future}=\frac{1}{7}\sum_{k=1}^{7}\widehat{DBP}_{t+k}
```

Word 公式输入：

```latex
DBP_{future}=\frac{1}{7}\sum_{k=1}^{7}\widehat{DBP}_{t+k}#(13)
```

## 公式（14）

LaTeX 公式本体：

```latex
Accuracy=\frac{TP+TN}{TP+TN+FP+FN}
```

Word 公式输入：

```latex
Accuracy=\frac{TP+TN}{TP+TN+FP+FN}#(14)
```

## 公式（15）

LaTeX 公式本体：

```latex
Precision=\frac{TP}{TP+FP}
```

Word 公式输入：

```latex
Precision=\frac{TP}{TP+FP}#(15)
```

## 公式（16）

LaTeX 公式本体：

```latex
Recall=\frac{TP}{TP+FN}
```

Word 公式输入：

```latex
Recall=\frac{TP}{TP+FN}#(16)
```

## 公式（17）

LaTeX 公式本体：

```latex
F1=\frac{2\times Precision\times Recall}{Precision+Recall}
```

Word 公式输入：

```latex
F1=\frac{2\times Precision\times Recall}{Precision+Recall}#(17)
```

## 公式（18）

LaTeX 公式本体：

```latex
Brier=\frac{1}{N}\sum_{i=1}^{N}(p_i-y_i)^2
```

Word 公式输入：

```latex
Brier=\frac{1}{N}\sum_{i=1}^{N}(p_i-y_i)^2#(18)
```

## 公式（19）

LaTeX 公式本体：

```latex
X_{bp}^{future}=\left[\frac{1}{7}\sum_{k=1}^{7}\widehat{SBP}_{t+k},\frac{1}{7}\sum_{k=1}^{7}\widehat{DBP}_{t+k}\right]
```

Word 公式输入：

```latex
X_{bp}^{future}=\left[\frac{1}{7}\sum_{k=1}^{7}\widehat{SBP}_{t+k},\frac{1}{7}\sum_{k=1}^{7}\widehat{DBP}_{t+k}\right]#(19)
```

## 公式（20）

LaTeX 公式本体：

```latex
\begin{aligned} \mathbf{x}_{LGBM}=&(male,age,smoker,cigsPerDay,BPMeds,diabetes,\\ &totChol,SBP_{future},DBP_{future},BMI,heartRate,glucose),\\ p_{raw}=&F_{LGBM}(\mathbf{x}_{LGBM}) \end{aligned}
```

Word 公式输入：

```latex
\begin{aligned} \mathbf{x}_{LGBM}=&(male,age,smoker,cigsPerDay,BPMeds,diabetes,\\ &totChol,SBP_{future},DBP_{future},BMI,heartRate,glucose),\\ p_{raw}=&F_{LGBM}(\mathbf{x}_{LGBM}) \end{aligned}#(20)
```

## 公式（21）

LaTeX 公式本体：

```latex
r_{high}=\frac{1}{7}\sum_{k=1}^{7}\mathbb{I}(\widehat{SBP}_{t+k}\ge140\ \text{or}\ \widehat{DBP}_{t+k}\ge90)
```

Word 公式输入：

```latex
r_{high}=\frac{1}{7}\sum_{k=1}^{7}\mathbb{I}(\widehat{SBP}_{t+k}\ge140\ \text{or}\ \widehat{DBP}_{t+k}\ge90)#(21)
```

## 公式（22）

LaTeX 公式本体：

```latex
s_{SBP}=\widehat{SBP}_{t+7}-\widehat{SBP}_{t+1},\quad s_{DBP}=\widehat{DBP}_{t+7}-\widehat{DBP}_{t+1}
```

Word 公式输入：

```latex
s_{SBP}=\widehat{SBP}_{t+7}-\widehat{SBP}_{t+1},\quad s_{DBP}=\widehat{DBP}_{t+7}-\widehat{DBP}_{t+1}#(22)
```

## 公式（23）

LaTeX 公式本体：

```latex
\Delta_{trend}=\min(0.08,0.08r_{high})+0.02I_{peak}+0.02I_{up}-0.02I_{stable}
```

Word 公式输入：

```latex
\Delta_{trend}=\min(0.08,0.08r_{high})+0.02I_{peak}+0.02I_{up}-0.02I_{stable}#(23)
```

## 公式（24）

LaTeX 公式本体：

```latex
p_{fused}=clip(p_{raw}+\Delta_{trend}+\Delta_{med},0.01,0.99)
```

Word 公式输入：

```latex
p_{fused}=clip(p_{raw}+\Delta_{trend}+\Delta_{med},0.01,0.99)#(24)
```

## 公式（25）

LaTeX 公式本体：

```latex
Level(p)= \begin{cases} 低风险,&p<0.30\\ 中风险,&0.30\le p<0.60\\ 高风险,&p\ge0.60 \end{cases}
```

Word 公式输入：

```latex
Level(p)= \begin{cases} 低风险,&p<0.30\\ 中风险,&0.30\le p<0.60\\ 高风险,&p\ge0.60 \end{cases}#(25)
```
