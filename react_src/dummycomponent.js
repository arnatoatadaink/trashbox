
class DummyComponent extends React.Component {
    constructor(props) {
        super(props);
    }
    componentDidMount(){
        // コンポーネントがマウントされた（ツリーに挿入された）直後に呼び出されます
    }
    componentDidUpdate(prevProps, prevState, snapshot){
        // 更新が行われた直後に呼び出されます。このメソッドは最初のレンダーでは呼び出されません
    }
    componentWillUnmount(){
        // コンポーネントが破棄される直前に呼び出されます
    }
    shouldComponentUpdate(nextProps, nextState){
        // 新しい props または state が受け取られると、レンダーする前に呼び出されます
    }
    static getDerivedStateFromProps(props, state){
        // 
    }
    static getDerivedStateFromError(error){
        // 子孫コンポーネントによってエラーがスローされた後に呼び出されます
    }
    getSnapshotBeforeUpdate(prevProps, prevState){
        // 最後にレンダーされた出力が DOM などにコミットされる直前に呼び出されます
    }
    componentDidCatch(error, info){
        // 子孫コンポーネントによってエラーがスローされた後に呼び出されます
    }
    render(){
        return (<></>);
    }
}
