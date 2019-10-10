Vue.component('modal', {
    template: '#modal-template',
    data: function () {
        return {
          text: '',
          block_id: null,
        };
    },
    methods: {
        close: function () {
            this.$emit('close');
            this.text = '';
        },
    }
})

Vue.component('daily', {
    methods: {
        getTimeStr(block) {
            return moment(block.time_start).format('H[h]mm')
        },
    },
    props: ["transaction"],
    template: `
    <table>
        <tr>
            <td> {{ transaction.source }} -> {{ transaction.destination }} </td>
            <td> {{ transaction.amount }} </td>
            <td> {{ getTimeStr(transaction) }} </td>
        </tr>
        <tr>
            <td colspan="2"> {{ transaction.text }} </td>
            <td> {{ transaction.status }} </td>
        </tr>
        </table>
    `
})

new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        transactions: [],
        newText: '',
        dest: 1,
        amount: 0,
        showNewModal: false,
    },
    methods: {
        getAll: function () {
            axios
              .get('/lbcflba/api/all')
              .then(response => (this.transactions = response.data))
              .catch(error => printerr("getAll"));
        },
        newTransaction: function () {
            axios.post('/lbcflba/api/new',
                       {'dest': this.dest, 'text': this.newText, 'amount': this.amount},
                       {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getAll()))
            .catch(error => this.printerr("status: " + error.response.status + "\n" + error.response.data))
            .then(() => {
                this.newText = '';
                this.showNewModal = false;
            });
        },
//        deleteBlock: function () {
//            axios.post('/tt/api/blocks/delete', {'pk': this.idToDelete}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
//            .then(response => (this.getShit()))
//            .catch(error => this.printerr())
//            .then(() => {
//                this.idToDelete = null;
//                this.showModifyModal = false;
//            });
//        },
        test: function () {
            alert("testing testing");
        },
        printerr: function (err_msg) {
            alert("fail...\n" + err_msg);
        }
    },
    mounted() {
        this.getAll();
    }
})